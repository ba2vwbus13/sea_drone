import Jetson.GPIO as GPIO
import time

print('start thruster!')

def ratio_to_duty(ratio):
    #https://discuss.bluerobotics.com/t/controlling-esc-with-jetson-xavier-python/10013/2
    duty = (1100+ratio*800)/1000000 * pwm_frequency * 100
    return duty

if __name__ == '__main__':
    output_pin = 32
    output_pin = 33
    pwm_frequency = 50#Hz
    # Pin Setup:
    # Board pin-numbering scheme
    GPIO.setmode(GPIO.BOARD)
    # set pin as an output pin with optional initial state of HIGH
    GPIO.setup(output_pin, GPIO.OUT, initial=GPIO.HIGH)
    p = GPIO.PWM(output_pin, pwm_frequency)

    ratio = 0.5#% 0=forward 0.5=stop 1=backward
    p.start(ratio_to_duty(ratio))
    print('start at {}'.format(ratio))
    incr = 0.1
    print("PWM running. Press CTRL+C to exit.")
    try:
        while True:
            time.sleep(6)
            if ratio >= 0.7 or ratio <= 0.3:
                incr = -incr
            ratio += incr
            p.ChangeDutyCycle(ratio_to_duty(ratio))
            print('change at {}'.format(ratio))
    finally:
        p.stop()
        GPIO.cleanup()