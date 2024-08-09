#!/usr/bin/env python
import Jetson.GPIO as GPIO
import rospy
from sensor_msgs.msg import Joy
from std_msgs.msg import Float32

class Controller:
    def __init__(self):
        rospy.init_node('controller')
        self.pwm_frequency = 50#Hz
        output_pin_L = 33
        output_pin_R = 32
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(output_pin_L, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(output_pin_R, GPIO.OUT, initial=GPIO.HIGH)
        self.pwm_L = GPIO.PWM(output_pin_L, self.pwm_frequency)
        self.pwm_R = GPIO.PWM(output_pin_R, self.pwm_frequency)
        self.pwm_L.start(self.ratio_to_duty_L(0.5)) #0=forward 0.5=stop 1=backward
        self.pwm_R.start(self.ratio_to_duty_R(0.5)) #0=forward 0.5=stop 1=backward
        self.sub = rospy.Subscriber('joy', Joy, self.joy_callback)
        rospy.on_shutdown(self.shutdown_callback)
        rospy.Timer(rospy.Duration(0.1), self.timer_callback) #0.1:waitが短すぎると動かないかもしれない
        self.linear_L = 0
        self.linear_R = 0 
    
    def joy_callback(self, joy_msg):
        self.linear_L = joy_msg.axes[1]
        self.linear_R = joy_msg.axes[5]
        rospy.loginfo('(joy) left = %f right = %f', self.linear_L , self.linear_R)

    def ratio_to_duty_L(self, ratio):
        ratio = max(min(ratio, 0.7), 0.3)
        #https://discuss.bluerobotics.com/t/controlling-esc-with-jetson-xavier-python/10013/2
        duty = (1900-(ratio*800))/1000000 * self.pwm_frequency * 100
        rospy.loginfo('(left) ratio = %f duty = %f', ratio, duty)
        return duty

    def ratio_to_duty_R(self, ratio):
        ratio = max(min(ratio, 0.7), 0.3)
        #https://discuss.bluerobotics.com/t/controlling-esc-with-jetson-xavier-python/10013/2
        duty = (1900-(ratio*800))/1000000 * self.pwm_frequency * 100
        rospy.loginfo('(right) ratio = %f duty = %f', ratio, duty)
        return duty

    def timer_callback(self, event):
        ratio = (self.linear_L+1.0)/2.0
        rospy.loginfo('pwm Left  %f', ratio)
        self.pwm_L.ChangeDutyCycle(self.ratio_to_duty_L(ratio))

        ratio = (self.linear_R+1.0)/2.0
        rospy.loginfo('pwm Right %f', ratio)
        self.pwm_R.ChangeDutyCycle(self.ratio_to_duty_R(ratio))

        
    def shutdown_callback(self):
        rospy.loginfo('Stop')
        self.pwm_L.ChangeDutyCycle(self.ratio_to_duty_L(0.5))#% 0=forward 0.5=stop 1=backward
        self.pwm_R.ChangeDutyCycle(self.ratio_to_duty_R(0.5))#% 0=forward 0.5=stop 1=backward
        self.pwm_L.stop()
        self.pwm_R.stop()
        rospy.sleep(1)
        GPIO.cleanup()

if __name__ == '__main__':

    rospy.loginfo('joy start')
    Controller()
    rospy.spin()