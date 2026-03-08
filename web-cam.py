##################################
# MLX90640 Test with Raspberry Pi
##################################
import time, board, busio
import numpy as np
import matplotlib as mpl
from scipy.ndimage import zoom
import adafruit_mlx90640
from PIL import Image
from io import BytesIO
from flask import Flask, Response, request, jsonify
import argparse

parser = argparse.ArgumentParser(description = 'Stream images from MLX90640 thermal camera.')
parser.add_argument('--ip', type=str, default='127.0.0.1', help='This hosts IP address to pass to Flask.')
args = parser.parse_args()

app = Flask(__name__)

N_ROWS = 24
N_COLS = 32
mlx_shape = (N_ROWS, N_COLS)

# Mutable bounds — updated by the form
bounds = {'min': 20.0, 'max': 250.0, 'log': False}
temp_range = {'min': 0, 'max': 0}
# log_transform = False
# log_radio = ''
# linear_radio = 'checked'

i2c = busio.I2C(board.SCL, board.SDA, frequency=400000)
mlx = adafruit_mlx90640.MLX90640(i2c)
mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_2_HZ

def generate_frames():
    cmap = mpl.colormaps['plasma']
    while True:
        frame = np.zeros((N_ROWS * N_COLS,))
        while True:
            try:
                mlx.getFrame(frame)
                break
            except ValueError:
                continue

        temp_range['min'], temp_range['max'] = np.min(frame), np.max(frame)
        lo, hi = bounds['min'], bounds['max']

        if bounds['log']:
            frame = np.log10(frame)
            lo = np.log10(lo)
            hi = np.log10(hi)

        normalized_data = np.clip(
            (np.fliplr(np.reshape(frame, mlx_shape)) - lo) / (hi - lo),
            0.0, 1.0)

        upscaled_data = zoom(normalized_data, 4, order=1)
        rgba = cmap(upscaled_data)
        rgb = (rgba[:, :, :3] * 255).astype(np.uint8)
        rgb_image = Image.fromarray(rgb, 'RGB')

        # print("min: {0:3.2f}  max: {1:3.2f}  bounds: [{2}, {3}]".format(
        #     np.min(frame), np.max(frame), lo, hi))

        buf = BytesIO()
        rgb_image.save(buf, format='JPEG')
        jpg = buf.getvalue()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpg + b'\r\n')
        time.sleep(0.25)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/set_bounds', methods=['POST'])
def set_bounds():
    try:
        bounds['min'] = float(request.form['min_temp'])
        bounds['max'] = float(request.form['max_temp'])
        transform_type = str(request.form['transform_type'])
        print(transform_type)
    except (KeyError, ValueError):
        pass
    if transform_type == 'log':
        bounds['log'] = True
        # log_radio = 'checked'
        # linear_radio = ''
    elif transform_type == 'linear':
        bounds['log'] = False
        # log_radio = ''
        # linear_radio = 'checked'
    # print(log_transform)
    return index()

@app.route('/temps')
def temps():
    return jsonify(temp_range)

@app.route('/')
def index():
    return f'''
    <h1>MLX90640 Thermal Camera</h1>
    <div style="text-align:center;">
    <img src="/video_feed"><br><br>
    Measured Temps: <span id="temp_display">--</span><br><br>
    <form method="POST" action="/set_bounds">
        <fieldset>
        <legend>Normalization</legend>
        <label>Min temp: <input type="number" name="min_temp" value="{bounds['min']}" step="0.5"></label>
        &nbsp;
        <label>Max temp: <input type="number" name="max_temp" value="{bounds['max']}" step="0.5"></label>
        &nbsp;
        <br>Measurement range: -40&deg;C &mdash; +300&deg;C
        </fieldset>
        <fieldset>
            <legend>Transform</legend>
            <div>
                <input type="radio" id="linear" name="transform_type" value="linear" {'' if bounds['log'] else 'checked'}>
                <label for="linear">Linear</label>
            </div>
            <div>
                <input type="radio" id="log" name="transform_type" value="log" {'checked' if bounds['log'] else ''}>
                <label for="log">Logarithmic</label>
            </div>
        </fieldset>
        <button type="submit">Apply</button>
    </form>
    <script>
        setInterval(() => {{
            fetch('/temps')
                .then(r => r.json())
                .then(d => {{
                    document.getElementById('temp_display').textContent =
                        d.min.toFixed(2) + ' - ' + d.max.toFixed(2) + ' \u00B0C';
                }});
        }}, 500);
    </script>
    </div>
    '''

if __name__ == '__main__':
    app.run(debug=True, host=args.ip)
