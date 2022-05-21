# Project EcoTopia (prototype)

Automatic multifunctional robot (prototype)


# Introduction

The end goal of this project is to create a multifunctional robot which can be used by councils to autonomously clean up park footpaths making it safer for passers by, and automatically dispense grit in the Winter when ice is likely to form, to melt the ice to make it safer to walk.

This is an early prototype, and as such only one feature (dispensing grit) has been coded, but in the future we plan on completing this project to make it a complete robot.

## Parts used

- Raspberry Pi 4 (2GB)
- SG90 Servo
- Adafruit DHT11 Temperature Sensor
- Mini Breadboard
- HC-SR04 Ultrasonic Distance Sensor
- L298N motor Driver
- 4x Wheels
	> To make building the project easier, we took apart an Elegoo car kit and used the distance sensor, motor driver and wheels from there. The L298N Motor driver found in this kit has two extra ports for the wheels (but you can also use a 2-pin L298N motor driver by splitting the pins to power two wheels each).
	 
- 16GB Micro SD card
- Male-Female and Male-Male Jumper Wires
- Android phone
- Acrylic sheets (cut into shape with a laser cutter)
- 9V Battery

## Programming languages used

- Python

## Setup instructions

1. Set up your Raspberry Pi with Raspberry Pi OS
2. Download the Adafruit_Python_DHT folder and save it to the Raspberry Pi's desktop
3. Open terminal (ctrl+alt+T), cd into Desktop/Adafruit_Python_DHT (`cd Desktop/Adafruit_Python_DHT`) and execute `sudo python3 setup.py install`
4. install Bluedot `pip3 install Bluedot`
5. Make a folder on Desktop called robot (`mkdir /home/pi/Desktop/robot`
6. Download `robot.py` and save it into the robot folder
7. Open `robot.py` and connect the parts together:
	- Take a jumper wire and connect the female part to the corresponding pin on the Pi (the numbers denote GPIO pins, not BCM pins), take a look at https://pinout.xyz/ to get the pinout
	- Connect the other end of the wire to the corresponding pin on the component (pinout should be labeled, if not then the red and black wires are for power and ground)
	- Take a female-male jumper wire and connect ground from the Pi to ground on the breadboard, and do the same for 5v
	- Connect the rest of the components to the breadboard's power and ground using male-male (or male-female) jumper wires
	- (Optional) Connect the LED to ground and it's corresponding pin
8. Connect the ground from the (9V battery to the breadboard's ground and then connect the breadboard's ground and the (V battery's power to the corresponding power/ground pins on the motor driver.
9. Connect the wheels to the ports on the motor driver
10. Pair your Android phone to the Pi via Bluetooth (required if you want to manually control the robot)
11. Install the Bluedot app from the Play Store on your Android device
12. Run `robot.py` and the file should start running

## App Controls

The app is set up to function as a d-pad, where you can tap and hold the top and bottom of the dot for the robot to move forwards and backwards, or left and right of the dot to make the robot spin. 

Double tapping anywhere on the dot except the top would cause the robot to switch from "manual" control to "automatic" control in which the robot would continuously travel forwards until it detects an object in the way, after which it would move back a tiny bit, turn and carry on moving forwards, and tapping and holding the button on "automatic" control causes the robot to stop.

Double tapping on the top of the dot initiates the shutdown prompt, doing this action 4 more times causes the Pi to shutdown, double tapping anywhere else after initiating the shutdown prompt aborts the shutdown.

The servo has been coded to only open/close if the robot is moving (i.e. if the dot is pressed in manual control, or if it isn't pressed while in automatic control).

## (Optional) Configure auto-start

If you want to configure your robot to automatically start executing the script you'll need to use crontab to get the file to run after the Pi turns on. 

1. Open terminal (Ctrl+Alt+T)
2. enter `crontab -e` 
	>If this is your first time entering this command, you'll be asked to choose which editor to use, you'll need to choose an editor then you will be able to edit the file that opens up.
3. Enter this code at the bottom of the file: `@reboot /usr/bin/sleep 30; while :; do  if [ $(/usr/bin/hcitool dev | /usr/bin/grep -c hci0) -gt 0 ]; then /usr/bin/sleep 10; /usr/bin/python3 /home/pi/Desktop/robot/robot.py & > /home/pi/Desktop/robot/robot.log 2>&1; break; else /usr/bin/sleep 1; fi; done`
	>What this command in the crontab does is that it waits for 30 seconds (to get everything to load up) then waits for the Bluetooth adapter to initialise, after which the Python program runs after 10 seconds.
5. Reboot to test if it works: `sudo reboot`
	>  If you connected the LED, it should start blinking once the Python script is running, if you haven't then you'll be able to tell when the script is running if you're able to connect to the Pi on the Bluedot app and the dot is visible.

## Team members in this project

- Muhammad Afzal Ali
- Alexander Samuel Roberts
- Harpreet Singh
- Ajay Mahey
- Zavier Moore


# External links

- https://pinout.xyz/ (View the pinout of the Pi GPIO pins)
- https://bluedot.readthedocs.io/en/latest/ (Documentation of Bluedot and its features)
- https://github.com/adafruit/Adafruit_Python_DHT (Library used to get the temperature sensor to function)
- https://www.elegoo.com/products/elegoo-smart-robot-car-kit-v-3-0-plus (Car kit used for distance sensor, motor driver and wheels)

