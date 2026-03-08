##################################
# MLX90640 Test with Raspberry Pi
##################################
#
import time,board,busio
import numpy as np
import adafruit_mlx90640
import os, time

N_ROWS = 24
N_COLS = 32
mlx_shape = (N_ROWS, N_COLS)
MIN_TEMP = 20
MAX_TEMP = 250
TEMP_TRANS_SLOPE = 255/(MAX_TEMP - MIN_TEMP)
TEMP_TRANS_INTERCEPT = MIN_TEMP

i2c = busio.I2C(board.SCL, board.SDA, frequency=400000) # setup I2C
mlx = adafruit_mlx90640.MLX90640(i2c) # begin MLX90640 with I2C comm
mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_2_HZ # set refresh rate

frame = np.zeros((N_ROWS*N_COLS,)) # setup array for storing all 768 temperatures

while True:
    while True:
        try:
            mlx.getFrame(frame) # read MLX temperatures into frame var
            break
        except ValueError:
            continue # if error, just read again

    data_array = (np.fliplr(np.reshape(frame, mlx_shape))) # reshape to 24x32
    data_array = np.round(data_array*TEMP_TRANS_SLOPE - TEMP_TRANS_INTERCEPT).astype(np.uint8)

    os.system('clear')
    for i in range(N_ROWS):
        row_text = ""
        for j in range(N_COLS):
            row_text += "{:3d}".format( data_array[i, j] )
            row_text += ' '
        print(row_text)
    print()
    time.sleep(0.3)
