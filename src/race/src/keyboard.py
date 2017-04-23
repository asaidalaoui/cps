#!/usr/bin/env python

import rospy
from race.msg import drive_param
import curses
#import signal
#TIMEOUT = 0.1 # number of seconds your want for timeout
forward = 0;
left = 0;

# def interrupted(signum, frame):
#     "called when read times out"
#     global forward
#     forward = 0
#     global left
#     left = 0
#     stdscr.addstr(2, 20, "Stop")
#     stdscr.addstr(2, 25, '%.2f' % forward)
#     stdscr.addstr(3, 20, "Stop")
#     stdscr.addstr(3, 25, '%.2f' % left)
# signal.signal(signal.SIGALRM, interrupted)

# def input():
#     try:
#             foo = stdscr.getch()
#             return foo
#     except:
#             # timeout
#             return

stdscr = curses.initscr()
curses.cbreak()
stdscr.keypad(1)
rospy.init_node('keyboard_talker', anonymous=True)
pub = rospy.Publisher('UI_drive_parameters', drive_param, queue_size=10)

# set alarm
#signal.alarm(TIMEOUT)
#s = input()
# disable the alarm after success
#signal.alarm(0)
#print 'You typed', s

stdscr.refresh()

key = ''
param = ""
while key != ord('q'):
#	signal.setitimer(signal.ITIMER_REAL,0.05)
#	key = input()
	stdscr.clrtoeol()
	stdscr.refresh()
	stdscr.addstr(2, 20, "Type s to select speed (0 to 50)\n")
	stdscr.addstr(5,20, "Type t to select angle (-100 to 100)\n")
	stdscr.addstr(8,20, "Type c to run in a circle\n")

	key = stdscr.getch()
#	signal.alarm(0)
	if key == ord('s'):
		stdscr.clrtoeol()
		stdscr.refresh()

		stdscr.addstr(2, 20, "Type s to select speed (0 to 50)\n")
		stdscr.addstr(5,20, "Type t to select angle (-100 to 100)\n")
		stdscr.addstr(8,20, "Type c to run in a circle\n")


		stdscr.addstr(11,20,"Enter the speed: ")
		param = stdscr.getstr()
		forward = int(param)
	
	elif key == ord('t'):
		
		stdscr.clrtoeol()
		stdscr.refresh()
		stdscr.addstr(2,20, "Enter the angle: ")
		param = stdscr.getstr()
		left = int(param)
		
	elif key == ord('c'):
		forward = 1
		left = 100

	else:
		continue

	msg = drive_param()
	msg.velocity = forward
	msg.angle = left
	pub.publish(msg)
curses.endwin()
