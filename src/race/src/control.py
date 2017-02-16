#!/usr/bin/env python

import rospy
from race.msg import drive_param
from race.msg import pid_input
import time

kp = .8
kd = .8
servo_offset = 18.5
prev_error = 0.0
vel_input = 50
n = 0
angle = 0

pub = rospy.Publisher('drive_parameters', drive_param, queue_size=1)

'''
    the on(n) and off(n) functions take a parameter 0 <= n <= 50
    and linearly approximate a velocity using a linear regression
    where the value n = 1 represents the lowest on/off time ratio
    that allows the car to move consistently and reliably.

    as n approaches 50, less time is spent sleeping with the motor off
    and more time sleeping with the motor on.

'''
# calculate time on while the motor is powered
def on(n):
	if (n == 0):
		return 0
	else:
		return 0.001429 * n + 0.06857

# calculate time off while motor is not powered
def off(n):
	if (n == 50):
		return 0
	elif (n == 0):
		return 1
	else:
        return -0.001429*n + 0.07143

def stateUpdater(data):
	global n
	global angle
	print ("state updater")
	n = data.velocity
	angle = data.angle

def control():

	global prev_error
	global vel_input
	global kp
	global kd
	global n
	global angle

	msg = drive_param();

	while not rospy.is_shutdown():
		msg.angle = angle
		msg.velocity = 10
		pub.publish(msg)
		# sleep motor on
		time.sleep(on(n))

		msg.velocity = 0
		pub.publish(msg)
		# sleep motor off
		time.sleep(off(n))

if __name__ == '__main__':
	rospy.init_node('pid_controller', anonymous=True)
	rospy.Subscriber("UI_drive_parameters", drive_param, stateUpdater)
	control()
	rospy.spin()
