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

pub = rospy.Publisher('drive_parameters', drive_param, queue_size=1)


def on(n):
    return 0.001429 * n + 0.06857

def off(n):
	if (n == 50):
		return 0	

    	return -0.001429*n + 0.07143



def control(data):
	global prev_error
	global vel_input
	global kp
	global kd

	## Your code goes here
	# 1. Scale the error
	# 2. Apply the PID equation on error
	# 3. Make sure the error is within bounds
#	angle = data.pid_error*kp;
#	if angle > 100:
#		angle = 100
#	if angle < -100:
#		angle = -100

	# circle parameters :
	# sleep while running = .08
	# sleep while stopped = .1
	# angle = 100 / -100

	# slow straighline parameters:
	# sleep while running = .07
	# sleep while stopped = .07
	# angle = 16.5 

	msg = drive_param();

	n = 49

	msg.angle = 4	
#	msg.velocity = 50
#	pub.publish(msg)
	while not rospy.is_shutdown():
		msg.velocity = 10
		pub.publish(msg)
		# sleep motor on
		time.sleep(on(n))

		msg.velocity = 0 
		pub.publish(msg)
		# sleep motor off
		time.sleep(off(n))
		

	#if(data.pid_vel == 0):
	#	msg.velocity = -8
	#else:
	#	msg.velocity = vel_input	

if __name__ == '__main__':
	rospy.init_node('pid_controller', anonymous=True)
	rospy.Subscriber("error", pid_input, control)
	rospy.spin()
