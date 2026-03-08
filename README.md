# MLX90640 Thermal Camera

I couldn't make work any of the projects I found online for the MLX90640, so I cobbled this together as a way to view images.  
It uses Adafruit I2C libraries to communicate with the camera, and streams color images through a Flask web server.
Note that there is a log transform available, but no accomodation is made for negative temperatures, so it will likely fail.

# Resources
- [MLX90640 Data sheet](https://www.melexis.com/en/product/mlx90640/far-infrared-thermal-sensor-array)
- [MakerPortal](https://makersportal.com/blog/2020/6/8/high-resolution-thermal-camera-with-raspberry-pi-and-mlx90640)
- [Adafruit project](https://learn.adafruit.com/raspberry-pi-thermal-camera)
- [PiThermalCam](https://tomshaffner.github.io/PiThermalCam/)
