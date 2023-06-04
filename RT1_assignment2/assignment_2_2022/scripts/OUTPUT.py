#!/usr/bin/env python3

"""
.. module:: OUTPUT
    :platform: Ubuntu
    :synopsis: Python module for controlling the turtlesim.

.. moduleauthor:: AHMET SAMET KOSUM

ROS node for controlling the robot.

Subscribes to:
    /posxy_velxy

Publishes to:
    /my_turtle/cmd_vel

Parameters:
    frequency (float): the frequency of the information printed in Hz.
    des_pos_x (float): the desired x position of the robot.
    des_pos_y (float): the desired y position of the robot.
"""

import rospy
import math
import time
from assignment_2_2022.msg import Posxy_velxy
from colorama import init
init()
from colorama import Fore, Back, Style


class PrintInfo:
    """
    Class for printing the distance and average speed of the robot to the desired position.
    """

    def __init__(self):
        """
        Constructor method.
        """
        self.F = rospy.get_param("frequency") # Get the publish frequency parameter
        self.LASTTIME = 0 # Last time the info was printed

        # Subscriber to the position and velocity topic
        self.sub_pos = rospy.Subscriber("/posxy_velxy", Posxy_velxy, self.posvel_callback)

    def posvel_callback(self, msg):
        """
        Callback function to print the distance and average speed of the robot.
        
        Args:
            msg (Posxy_velxy): the message containing the robot's position and velocity.
        """

        P = (1.0/self.F) * 1000         # Compute time period in milliseconds
        CURRRENTTIME = time.time() * 1000         # Get current time in milliseconds

        # Check if the current time minus the last printed time is greater than the period
        if CURRRENTTIME - self.LASTTIME > P:
            # Get the desired position from ROS parameters
            X_TARGET = rospy.get_param("des_pos_x")
            Y_TARGET = rospy.get_param("des_pos_y")

            # Get the actual position of the robot from the message
            robot_x = msg.msg_pos_x
            robot_y = msg.msg_pos_y

            # Compute the distance between the desired and actual positions
            DIST = round(math.dist([X_TARGET, Y_TARGET], [robot_x, robot_y]),2)

            # Get the actual velocity of the robot from the message
            vel_x = msg.msg_vel_x
            vel_y = msg.msg_vel_y           

            # Compute the average speed using the velocity components from the message
            average_speed = round(math.sqrt(vel_x**2 + vel_y**2),2)

            # Print the distance and speed information
            print(Fore.BLUE + f"Distance to Target: {DIST} [m]")
            print(Fore.RED + f"The Average Speed of Robot: {average_speed} [m/s]")

            # Update the last printed time
            self.LASTTIME = CURRRENTTIME


def main():
    """
    Main method for initializing the node and creating an instance of PrintInfo class.
    """
    # Initialize the node
    rospy.init_node('OUTPUT')

    # Create an instance of the PrintInfo class
    OUTPUT = PrintInfo()

    # Wait for messages
    rospy.spin()


if __name__ == "__main__":
    main()


