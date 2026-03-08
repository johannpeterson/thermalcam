# MLX90640 Thermal Camera

## Introduction

I couldn't make work any of the projects I found online for the MLX90640, so I cobbled this together as a way to view images.  It uses Adafruit I2C libraries to communicate with the camera, and streams color images through a Flask web server.

## Usage

The main script is `web-cam.py`.

Once the virual environment has been created and libraries installed on a Raspberry Pi:
```bash
source env/bin/activate
sudo -E env PATH=$PATH python web-cam.py --ip '192.168.x.x'
```
For a guide to setting up the Raspberry Pi, see the [Adafruit documentation](https://learn.adafruit.com/raspberry-pi-thermal-camera/installing-circuitpython-on-raspberry-pi).

## Notes

1. The host IP address should be passed on the command line.  If the
argument is omitted, the server will be available only on the local
127.0.0.1 IP.

2. Note that there is a log transform available, but no accomodation is made for negative temperatures, so it will probably fail.

## Resources
- [MLX90640 Data sheet](https://www.melexis.com/en/product/mlx90640/far-infrared-thermal-sensor-array)
- [MakerPortal](https://makersportal.com/blog/2020/6/8/high-resolution-thermal-camera-with-raspberry-pi-and-mlx90640)
- [Adafruit project](https://learn.adafruit.com/raspberry-pi-thermal-camera)
- [PiThermalCam](https://tomshaffner.github.io/PiThermalCam/)
