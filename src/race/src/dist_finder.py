#!/usr/bin/env python

import rospy
import math
from sensor_msgs.msg import LaserScan
from race.msg import pid_input
from std_msgs.msg import String

desired_trajectory = 1
vel = 30

pub = rospy.Publisher('error', pid_input, queue_size=10)
distPub = rospy.Publisher('distance', String)
frontDistPub = rospy.Publisher('front_distance', String)

##	Input: 	data: Lidar scan data
##			theta: The angle at which the distance is requried
##	OUTPUT: distance of scan at angle theta
def getRange(data,theta):
# Find the index of the arary that corresponds to angle theta.
# Return the lidar scan value at that index
# Do some error checking for NaN and ubsurd values
## Your code goes here
  distance = data.ranges[theta]
  if math.isnan(distance) or distance > 2.5:
    distance = 50
  return distance

def callback(data):
	"""
  theta = 360;
	a = getRange(data,theta)
	b = getRange(data,0)
	swing = math.radians(theta)
	
	## Your code goes here

	error = a-b
	if(getRange(data,540)<.75):
		vel = 0
	else:
		vel = 8
  if getRange(data, 360) > 5: # Wide turn
    error = -100
  if getRange(data,360) > 5:
    error = 100
  else:
    b = 50
    c = 50
    for i in range(170, 450, 10):
      b2 = getRange(i)*math.cos(math.radians((i-180)/4))
      if b2<b:
        b = b2
        c = getRange(i)*math.sin(math.radians((i-180)/4))

    error = (b-.5)/c
	"""

	sum = 0
#	print(data.intensities[180])
	for i in range(180, 500, 10):
    #if(data.intensities[i]<.9):
		sum += (getRange(data,i)*math.cos(math.radians((i-180)/4))-.50)/getRange(data,i)*math.sin(math.radians((i-180)/4))
    #else:
    # sum = sum + (getRange(data,i)*math.cos(math.radians((i-180)/4))-.5-getRange(180)-getRange(900))/getRange(data,i)*math.sin(math.radians((i-180)/4))
		#print (getRange(data,360))
	error = sum / 36

	# side distance
	d = getRange(data,400)	

	# front distance
	f_d = getRange(data,540)

	print  "side dist: " + str(d) + " front dist: "  +" "+ str(f_d)
	print(error)	

	if(d<.75):
		vel = 0
	else:
		vel = 8

	msg2 = String()
	msg2.data = str(d)

	front_dist = String()
	front_dist.data = str(f_d)

	distPub.publish(msg2)
	frontDistPub.publish(front_dist)
	

	msg = pid_input()
	msg.pid_error = error
	msg.pid_vel = vel
	pub.publish(msg)
	

if __name__ == '__main__':
	print("Laser node started")
	rospy.init_node('dist_finder',anonymous = True)
	rospy.Subscriber("scan",LaserScan,callback)
	rospy.spin()
