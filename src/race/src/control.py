#!/usr/bin/env python

import rospy
from race.msg import drive_param
from race.msg import pid_input
import time
from std_msgs.msg import String, Float32
import math

kp = 170
kd = 3
servo_offset = 18.5
prev_error = 0.0 
vel_input = 25
n = 0
angle = 0
circleDetected = False
detected_rad = 0
distance = 0.0
front_d = 0.0
state_counter = 0
circle_speed = 0
pub = rospy.Publisher('drive_parameters', drive_param, queue_size=1)
previous = 0
current = 0

def circleCallback (sig):
	global circleDetected
	global detected_rad
	global state_counter
	global circle_speed

	if sig.data == "Not Detected":
		circleDetected = False
	else:
		circle_data = str(sig.data).split(" ")
		circleDetected = True
		detected_rad = float(circle_data[1])
				
def check_distance ():
	global distance
	return distance > 1.0

def check_front_distance ():
	global front_dist
	return front_dist < 1.25

def front_distance (data):
	global front_dist	
	front_dist = float(data.data)

def control():
	
	global prev_error
	global vel_input
	global kp
	global kd
	global n
	global angle
	global circle_speed

	## Your code goes here
	# 1. Scale the error
	# 2. Apply the PID equation on error
	# 3. Make sure the error is within bounds
	#print ("angle", angle)
	if angle > 100:
		angle = 100
	if angle < -100:
		angle = -100

	msg = drive_param();
	
	#if(n == 0 and not circleDetected):
	#	print("STOP")
	#	msg.velocity = n
	#	msg.angle = angle

	#print (str(circleDetected) + " " + str(front_dist <.50))
	if (check_front_distance() and circleDetected):
		print("TURN LEFT")
		msg.velocity = circle_speed
		msg.angle = -100
	else:
		msg.velocity = circle_speed
		# note 17 is for car 1 because nobody calibrates these wheels.
		#print "angle before transform ", str(angle)
		#if angle > 1 and angle < 4:
		#	msg.angle = math.pow(3,angle)
		#else:
		msg.angle = angle
		#print "SLOW DOWN"
#	else:
#		print("FORWARD")
#		msg.velocity = n
#		msg.angle = angle 
	
	#print "msg.vel = " + str(msg.velocity) + " angle = " + str(msg.angle ) + " distance " + str(distance) + " front dist " + str(front_dist)
	pub.publish(msg)

def stateUpdater(data):
	global n
	global angle
	global previous
	global current
	global state_counter
	global circle_speed
	global distance

	n = data.pid_vel
	previous = current
	current = data.pid_error
	angleD = (previous - current)*kd	
	angle = 100 if check_distance() else data.pid_error*kp + angleD
	print " angle : " + str(angle) + " distance " + str(distance)
	if state_counter < 0:
		circle_speed = -8
	else:
		circle_speed = 8
	state_counter += 1
	state_counter = -7 if state_counter == 13 else state_counter
#if angle > 2:
	#	angle = 50
	
def velocityCallback(data):
	global distance
	distance = float(data.data)
	control()
	

if __name__ == '__main__':
	rospy.init_node('pid_controller', anonymous=True)
	rospy.Subscriber("error", pid_input, stateUpdater)
	rospy.Subscriber("circle_chatter", String, circleCallback)
	rospy.Subscriber("front_distance", String, front_distance)
	rospy.Subscriber("distance", String, velocityCallback)
	rospy.spin()
