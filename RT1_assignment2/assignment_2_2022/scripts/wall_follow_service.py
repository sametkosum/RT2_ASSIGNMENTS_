#!/usr/bin/env python3

"""
.. module:: wall_folllow_service
   :platform: Ubuntu
   :synopsis: This node subscribes to LaserScan messages and publishes Twist messages to control the robot's velocity.


.. moduleauthor:: AHMET SAMET KOSUM

This ROS node controls the turtle robot using laser scans to detect obstacles
and follow walls.

Subscribes to:
    /scan (sensor_msgs/LaserScan)

Publishes to:
    /cmd_vel (geometry_msgs/Twist)

Clients:
    /wall_follower_switch (std_srvs/SetBool)
"""

import rospy
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from std_srvs.srv import SetBool
from std_srvs.srv import SetBoolResponse

import math

active_ = False
pub_ = None

regions_ = {
    'right': 0,
    'fright': 0,
    'front': 0,
    'fleft': 0,
    'left': 0,
}

state_ = 0
state_dict_ = {
    0: 'find the wall',
    1: 'turn left',
    2: 'follow the wall',
}

def wall_follower_switch(req):
    """Callback function to switch the wall follower on/off
    
    Args:
        req: A ROS service request object of type SetBool
    
    Returns:
        res: A ROS service response object of type SetBoolResponse
    """
    global active_
    active_ = req.data
    res = SetBoolResponse()
    res.success = True
    res.message = 'Done!'
    return res

def clbk_laser(msg):
    """Callback function for the LaserScan subscriber
    
    Args:
        msg: A ROS message of type LaserScan
    """
    global regions_
    regions_ = {
        'right':  min(min(msg.ranges[0:143]), 10),
        'fright': min(min(msg.ranges[144:287]), 10),
        'front':  min(min(msg.ranges[288:431]), 10),
        'fleft':  min(min(msg.ranges[432:575]), 10),
        'left':   min(min(msg.ranges[576:713]), 10),
    }
    take_action()

def change_state(state):
    """Function to change the state of the robot
    
    Args:
        state: The new state of the robot (integer)
    """
    global state_, state_dict_
    if state != state_:
        print ('Wall follower - [%s] - %s' % (state, state_dict_[state]))
        state_ = state


def take_action():
    """Function to determine the appropriate action for the robot based on its current state"""
    global regions_
    regions = regions_
    msg = Twist()
    linear_x = 0
    angular_z = 0
    state_description = ''

    d0 = 1
    d = 1.5

    if regions['front'] > d0 and regions['fleft'] > d and regions['fright'] > d:
        state_description = 'case 1 - nothing'
        change_state(0)
    elif regions['front'] < d0 and regions['fleft'] > d and regions['fright'] > d:
        state_description = 'case 2 - front'
        change_state(1)
    elif regions['front'] > d0 and regions['fleft'] > d and regions['fright'] < d:
        state_description = 'case 3 - fright'
        change_state(2)
    elif regions['front'] > d0 and regions['fleft'] < d and regions['fright'] > d:
        state_description = 'case 4 - fleft'
        change_state(0)
    elif regions['front'] < d0 and regions['fleft'] > d and regions['fright'] < d:
        state_description = 'case 5 - front and fright'
        change_state(1)
    elif regions['front'] < d0 and regions['fleft'] < d and regions['fright'] > d:
        state_description = 'case 6 - front and fleft'
        change_state(1)
    elif regions['front'] < d0 and regions['fleft'] < d and regions['fright'] < d:
        state_description = 'case 7 - front and fleft and fright'
        change_state(1)
    elif regions['front'] > d0 and regions['fleft'] < d and regions['fright'] < d:
        state_description = 'case 8 - fleft and fright'
        change_state(0)
    else:
        state_description = 'unknown case'
        rospy.loginfo(regions)


def find_wall():
    """Sets the robot's velocity to move forward and turn left.

    Returns:
        geometry_msgs.msg.Twist: The Twist message.
    """
    msg = Twist()
    msg.linear.x = 0.2
    msg.angular.z = -0.3
    return msg


def turn_left():
    """Sets the robot's velocity to turn left.

    Returns:
        geometry_msgs.msg.Twist: The Twist message.
    """
    msg = Twist()
    msg.angular.z = 0.3
    return msg


def follow_the_wall():
    """Sets the robot's velocity to follow the wall.

    Returns:
        geometry_msgs.msg.Twist: The Twist message.
    """
    global regions_

    msg = Twist()
    msg.linear.x = 0.5
    return msg


def main():
    """
    Main function that initializes the ROS node and sets up subscribers and publishers
    for the laser scan and robot velocity commands.
    """
    global pub_, active_

    rospy.init_node('reading_laser')

    pub_ = rospy.Publisher('/cmd_vel', Twist, queue_size=1)

    sub = rospy.Subscriber('/scan', LaserScan, clbk_laser)

    srv = rospy.Service('wall_follower_switch', SetBool, wall_follower_switch)

    rate = rospy.Rate(20)
    while not rospy.is_shutdown():
        if not active_:
            rate.sleep()
            continue
        else:
            msg = Twist()
            if state_ == 0:
                msg = find_wall()
            elif state_ == 1:
                msg = turn_left()
            elif state_ == 2:
                msg = follow_the_wall()
            else:
                rospy.logerr('Unknown state!')

            pub_.publish(msg)

        rate.sleep()


if __name__ == '__main__':
    main()
