from bluedot import BlueDot
from signal import pause
from time import sleep
from datetime import datetime
from random import randint
import time
import Adafruit_DHT
import threading
import RPi.GPIO as GPIO
import subprocess


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#GPIO pinout 
PIN_IN1 = 16 #Right motor pin 1
PIN_IN2 = 21 #Right motor pin 2
PIN_IN3 = 26 #Left motor pin 1
PIN_IN4 = 20 #Left motor pin 2
PIN_EN1 = 19 #Right motor PWM
PIN_EN2 = 6 #Left motor PWM
PIN_TEMP_SENSOR = 3 #Temperature sensor pin
PIN_TRIGGER = 4 #Ultrasonic Distance Sensor trigger pin
PIN_ECHO = 23 #Ultrasonic Distance Sensor echo pin
PIN_LED = 5 #PIN_LED pin
PIN_SERVO = 17 #Servo pin

GPIO.setup(PIN_IN1,GPIO.OUT)
GPIO.setup(PIN_IN2,GPIO.OUT)
GPIO.setup(PIN_IN3,GPIO.OUT)
GPIO.setup(PIN_IN4,GPIO.OUT)
GPIO.setup(PIN_EN1,GPIO.OUT)
GPIO.setup(PIN_EN2,GPIO.OUT)
GPIO.setup(PIN_LED,GPIO.OUT)
GPIO.setup(PIN_TRIGGER, GPIO.OUT)
GPIO.setup(PIN_ECHO, GPIO.IN)
GPIO.setup(PIN_SERVO,GPIO.OUT)

GPIO.output(PIN_IN1,GPIO.LOW)
GPIO.output(PIN_IN2,GPIO.LOW)
GPIO.output(PIN_IN3,GPIO.LOW)
GPIO.output(PIN_IN4,GPIO.LOW)


#Start motor PWMs
MOTOR_1=GPIO.PWM(PIN_EN1,200)
MOTOR_2=GPIO.PWM(PIN_EN2,200)
MOTOR_1.start(0)
MOTOR_2.start(0)

#Start servo PWM
SERVO = GPIO.PWM(17,50)
SERVO.start(0)

mode = [-1]
direction = [None, None]
start_temp_sensor = [0]
start_distance_sensor = [0]

servo_control = [0]
servo_open = [False]
servo_timer = [0]

ShutdownSequence = []

def log(*args):
    print(f"[{str(datetime.now().hour).zfill(2)}:{str(datetime.now().minute).zfill(2)}:{str(datetime.now().second).zfill(2)}]", *args)


def forwards():
    MOTOR_1.ChangeDutyCycle(100)
    MOTOR_2.ChangeDutyCycle(100)
    GPIO.output(PIN_IN1,GPIO.HIGH)
    GPIO.output(PIN_IN2,GPIO.LOW)
    GPIO.output(PIN_IN3,GPIO.LOW)
    GPIO.output(PIN_IN4,GPIO.HIGH)

def backwards():
    MOTOR_1.ChangeDutyCycle(100)
    MOTOR_2.ChangeDutyCycle(100)
    GPIO.output(PIN_IN1,GPIO.LOW)
    GPIO.output(PIN_IN2,GPIO.HIGH)
    GPIO.output(PIN_IN3,GPIO.HIGH)
    GPIO.output(PIN_IN4,GPIO.LOW)
    
def left():
    MOTOR_1.ChangeDutyCycle(100)
    MOTOR_2.ChangeDutyCycle(100)
    GPIO.output(PIN_IN1,GPIO.HIGH)
    GPIO.output(PIN_IN2,GPIO.LOW)
    GPIO.output(PIN_IN3,GPIO.HIGH)
    GPIO.output(PIN_IN4,GPIO.LOW)
    
def right():
    MOTOR_1.ChangeDutyCycle(100)
    MOTOR_2.ChangeDutyCycle(100)
    GPIO.output(PIN_IN1,GPIO.LOW)
    GPIO.output(PIN_IN2,GPIO.HIGH)
    GPIO.output(PIN_IN3,GPIO.LOW)
    GPIO.output(PIN_IN4,GPIO.HIGH)
    
def stop():
    MOTOR_1.ChangeDutyCycle(0)
    MOTOR_2.ChangeDutyCycle(0)
    

def switch():
    if mode[0] == 1:
        mode[0] = -1
        log("Switching to Manual mode")
    elif mode[0] == -1:
        mode[0] = 1
        log("Switching to Automatic mode")
    if bd.position.top:
        ShutdownSequence.append(1)
        tmp = 5-len(ShutdownSequence)
        if tmp > 0:
            log()
            log(f"Press {tmp} times to shutdown")
            log()
            for n in range(1,5):
                GPIO.output(PIN_LED,GPIO.HIGH)
                sleep(0.1)
                GPIO.output(PIN_LED,GPIO.LOW)
                sleep(0.1)
        else:
            log("Shutting down...")
            sleep(5)
            subprocess.run(["sudo", "shutdown", "-h", "now"])
    elif len(ShutdownSequence) > 0:
        ShutdownSequence.clear()
        log()
        log("Shutdown aborted")
        log()
        

def temp_sensor():
    while True:
        if start_temp_sensor[0] == 1:
            temperature = Adafruit_DHT.read(11, PIN_TEMP_SENSOR)[1]
            if temperature is not None:
                log(f"Temperature: {temperature}°C")
            elif temperature is None:
                log(f"Temperature: -°C")
        sleep(1)

def distance_sensor():
    
    while True:
        if start_distance_sensor[0] == 1 and mode[0] == 1 and not bd.is_pressed:
            servo_control[0] = 1
    
            GPIO.output(PIN_TRIGGER, GPIO.LOW)

            sleep(0.1)

            GPIO.output(PIN_TRIGGER, GPIO.HIGH)

            sleep(0.00001)

            GPIO.output(PIN_TRIGGER, GPIO.LOW)
            while GPIO.input(PIN_ECHO)==0:
                pulse_start_time = time.time()
            while GPIO.input(PIN_ECHO)==1:
                pulse_end_time = time.time()

            pulse_duration = (pulse_end_time - pulse_start_time)
            distance = round(pulse_duration * 17150, 2)
            if distance < 25:
              log(f"Distance: {distance}cm, adjusting position")
              log("Reversing...")
              backwards()
              sleep(0.5)
              log("Turning right...")
              right()
              sleep(0.5)
            else:
              log(f"Distance: {distance}cm, moving forwards")
              forwards()


def dispenser_servo():
    while True:
        if servo_control[0] == 1:
            servo_tmp = randint(1,100)
            if servo_tmp > 70:
                if servo_open[0] == False:
                    servo_timer[0] = 30
                    servo_open[0] = True
                    log("Servo opened")
                    SERVO.ChangeDutyCycle(2+(90/18))
                    sleep(1)
                    SERVO.ChangeDutyCycle(0)
                elif servo_open[0] == True and servo_timer[0] < 1:
                    servo_open[0] = False
                    log("Servo closed")
                    SERVO.ChangeDutyCycle(2+(0/18))
                    sleep(1)
                    SERVO.ChangeDutyCycle(0)
        if servo_timer[0] > 0:
            servo_timer[0]-=1
        sleep(1)
    

def drive():
    while True:
        if (bd.is_pressed and mode[0] == -1) or (not bd.is_pressed and mode[0] == 1):
            servo_control[0] = 1
        elif (not bd.is_pressed and mode[0] == -1) or (bd.is_pressed and mode[0] == 1):
            servo_control[0] = 0
            direction[1] = "stopped"
            if direction[0] != direction[1]:
                log("Robot stopped")
                direction[0] = "stopped"
            stop()
        if bd.is_pressed and mode[0] == -1:
            start_temp_sensor[0] = 1
            start_distance_sensor[0] = 0
            if bd.position.top:
                direction[1] = "top"
                if direction[0] != direction[1]:
                    log("Manual mode (moving forwards)")
                    direction[0] = "top"
                    forwards()
                GPIO.output(PIN_LED,GPIO.HIGH)
            elif bd.position.right:
                direction[1] = "right"
                if direction[0] != direction[1]:
                    log("Manual mode (turning right)")
                    direction[0] = "right"
                    right()
                GPIO.output(PIN_LED,GPIO.HIGH)
            elif bd.position.bottom:
                direction[1] = "bottom"
                if direction[0] != direction[1]:
                    log("Manual mode (reversing)")
                    direction[0] = "bottom"
                    backwards()
                GPIO.output(PIN_LED,GPIO.HIGH)
            elif bd.position.left:
                direction[1] = "left"
                if direction[0] != direction[1]:
                    log("Manual mode (turning left)")
                    direction[0] = "left"
                    left()
                GPIO.output(PIN_LED,GPIO.HIGH)
        elif not bd.is_pressed and mode[0] == 1:
            direction[1] = "top"
            if direction[0] != direction[1]:
                direction[0] = "top"

            start_distance_sensor[0] = 1

        
def flashing_led():
    while True:
        if (not bd.is_pressed and mode[0] == -1):
            delay = 1.5
            flash = True
        elif mode[0] == 1:
            delay = 0.5
            flash = True
        else:
            flash = False
            
        if flash:
            GPIO.output(PIN_LED,GPIO.HIGH)
            sleep(delay)
            GPIO.output(PIN_LED,GPIO.LOW)
            sleep(delay)


bd = BlueDot()  # MockBlueDot if testing without phone
bd.double_press_time = 0.4
#bd.launch_mock_app()  # Uncomment if testing without phone
bd.when_double_pressed = switch
drive_thread = threading.Thread(target=drive, name="Drive")
temperature_thread = threading.Thread(target=temp_sensor, name="Temp sensor")
distance_thread = threading.Thread(target=distance_sensor, name="Distance sensor")
LED_thread = threading.Thread(target=flashing_led, name="LED")
dispenser_thread = threading.Thread(target=dispenser_servo, name="Dispenser Servo")

drive_thread.start()
temperature_thread.start()
distance_thread.start()
LED_thread.start()
dispenser_thread.start()

pause()

