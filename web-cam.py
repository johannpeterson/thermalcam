##################################
# MLX90640 Test with Raspberry Pi
##################################
#

# source env/bin/activate
# sudo -E env PATH=$PATH python web-cam.py

import time,board,busio
import numpy as np
import matplotlib as mpl
from scipy.ndimage import zoom
import adafruit_mlx90640
import os, time
from PIL import Image
from io import BytesIO
from flask import Flask, Response

app = Flask(__name__)

N_ROWS = 24
N_COLS = 32
mlx_shape = (N_ROWS, N_COLS)
MIN_TEMP = 20
MAX_TEMP = 250
TEMP_TRANS_SLOPE = 1/(MAX_TEMP - MIN_TEMP)
TEMP_TRANS_INTERCEPT = MIN_TEMP

i2c = busio.I2C(board.SCL, board.SDA, frequency=400000) # setup I2C
mlx = adafruit_mlx90640.MLX90640(i2c) # begin MLX90640 with I2C comm
mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_2_HZ # set refresh rate


def generate_frames():
    cmap = mpl.colormaps['plasma']
    while True:
        # data_array = np.reshape( np.arange(100*100), (100, 100) )
        frame = np.zeros((N_ROWS*N_COLS,)) # setup array for storing all 768 temperatures
        # frame = np.reshape( np.arange(10000), (100, 100) ) # setup array for storing all 768 temperatures
        while True:
            try:
                mlx.getFrame(frame) # read MLX temperatures into frame var
                break
            except ValueError:
                continue # if error, just read again
        normalized_data = np.clip(
            (np.fliplr(np.reshape(frame, mlx_shape)) - MIN_TEMP)/(MAX_TEMP - MIN_TEMP),
            0.0, 1.0)
        upscaled_data = zoom(normalized_data, 4, order=1)
        rgba = cmap(upscaled_data)
        rgb = (rgba[:, :, :3] * 255).astype(np.uint8)
        # data_array = np.round(data_array*TEMP_TRANS_SLOPE - TEMP_TRANS_INTERCEPT).astype(np.uint8)

        # 2. Convert the NumPy array to a PIL Image object
        rgb_image = Image.fromarray(rgb, 'RGB')

        print("min temp: {0:3.2f} max temp: {1:3.2f} scaled to: {2:3.2f} - {3:3.2f}".format(
            np.min(frame), np.max(frame), np.min(normalized_data), np.max(normalized_data) ))

        # 3. Save the PIL image to a byte buffer (in memory)
        buf = BytesIO()
        rgb_image.save(buf, format='JPEG') # Choose format (JPEG for streaming)
        frame = buf.getvalue()

        # 4. Yield the frame in a multipart format
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        # Optional: Add a small delay for smoother streaming (adjust as needed)
        time.sleep(0.25)

@app.route('/video_feed')
def video_feed():
    """Route to serve the streaming video feed."""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    """Main page to display the stream."""
    return '<h1>NumPy Image Stream</h1><img src="/video_feed">'

if __name__ == '__main__':
    app.run(debug=True, host='192.168.4.110')
