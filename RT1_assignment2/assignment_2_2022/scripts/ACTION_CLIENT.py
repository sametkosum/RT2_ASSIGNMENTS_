#!/usr/bin/env python3

"""
Module: ACTION_CLIENT
Platform: Ubuntu
Synopsis:  it is a ROS node for controlling a robot that subscribes to "/odom" topic to get position and velocity information and publishes to "/posxy_velxy" topic. It also implements an action client to prompt the user to enter a target position or cancel the current goal and sends the goal to the action server and waits for a response.
Module author: AHMET SAMET KOSUM 

ROS node for controlling the robot. Subscribes to /odom and publishes to /posxy_velxy. Also implements an action client.


Subscribes to:
    /odom

Publishes to:
    /posxy_velxy

Clients:
    /reaching_goal
"""
import rospy
import actionlib
from std_srvs.srv import *
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Point, Pose, Twist
from assignment_2_2022.msg import Posxy_velxy
from assignment_2_2022.msg import PlanningAction, PlanningGoal

from colorama import Fore, Style, init
init()

def publisher(msg):
    """Callback function for the subscriber.

    Gets the position and velocity from the message, creates a custom message
    with these parameters, and publishes it.

    Args:
        msg (Odometry): The message received from the subscriber.

    Returns:
        None
    """
    global pub
    POSITION = msg.pose.pose.position
    VELOCITY = msg.twist.twist.linear
    posxy_velxy = Posxy_velxy()
    posxy_velxy.msg_pos_x = POSITION.x
    posxy_velxy.msg_pos_y = POSITION.y
    posxy_velxy.msg_vel_x = VELOCITY.x
    posxy_velxy.msg_vel_y = VELOCITY.y
    pub.publish(posxy_velxy)

def action_client():
    """Runs the action client.

    Prompts the user to enter a target position or cancel the current goal.
    Sends the goal to the action server and waits for a response.
    """
    # create the action client
    action_client = actionlib.SimpleActionClient('/reaching_goal', PlanningAction)

    # wait for the server to be started
    action_client.wait_for_server()

    while not rospy.is_shutdown():
        # Get the keyboard inputs
        print(Fore.WHITE + " Enter position of the target or type c to cancel it ")
        INPUT_XPOS = input(Fore.BLUE + "Desired X Position : ")
        INPUT_YPOS = input(Fore.BLUE + "Desired Y Position : ")

        if INPUT_XPOS == "c" or INPUT_YPOS == "c":
            # Cancel the goal if the user entered 'c'
            action_client.cancel_goal()
        else:
            try:
                # Convert input to float
                SEND_XPOS = float(INPUT_XPOS)
                SEND_YPOS = float(INPUT_YPOS)

                # Create the goal to send to the server
                goal = PlanningGoal()
                goal.target_pose.pose.position.x = SEND_XPOS
                goal.target_pose.pose.position.y = SEND_YPOS
                action_client.send_goal(goal)

                # Wait for the server to respond
                action_client.wait_for_result()

            except ValueError:
                print("Invalid input")

def main():
    """Initializes the ROS node and runs the action client."""
    rospy.init_node('ACTION_CLIENT')
    global pub
    pub = rospy.Publisher("/posxy_velxy", Posxy_velxy, queue_size=1)
    sub_from_Odom = rospy.Subscriber("/odom", Odometry, publisher)
    action_client()

if __name__ == '__main__':
    main()

