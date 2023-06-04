#!/usr/bin/env python3

"""
.. module:: TARGETSERVICE

   :platform: Ubuntu
   
   :synopsis: ROS service and actionlib implementation for reaching goals.

.. moduleauthor:: AHMET SAMET KOSUM


"""

import rospy  # Import the ROS python library
import actionlib  # Import the actionlib library
import actionlib.msg  # Import the actionlib message library
from assignment_2_2022.srv import goal_rc, goal_rcResponse  # Import the service and service response messages
import assignment_2_2022.msg  # Import the package message library
from geometry_msgs.msg import Twist  # Import the Twist message type


class Service:
    """
    This class provides a ROS service to get the number of goals reached and cancelled.

    Attributes:
        TARGET_CANCELLED (int): The number of targets that were cancelled.
        TARGET_REACHED (int): The number of targets that were reached.
        srv (rospy.Service): The ROS service that will provide the data.
        sub_result (rospy.Subscriber): The ROS subscriber for the result topic.
    """

    def __init__(self):
        """
        The constructor for the Service class.

        Initializes the counters for goals reached and cancelled,
        creates the service, and subscribes to the result topic.
        """
        self.TARGET_CANCELLED = 0
        self.TARGET_REACHED = 0

        self.srv = rospy.Service('TARGETSERVICE', goal_rc, self.data)
        self.sub_result = rospy.Subscriber('/reaching_goal/result',
                                           assignment_2_2022.msg.PlanningActionResult,
                                           self.result_callback)

    def result_callback(self, msg):
        """
        A callback function that updates the number of targets reached and cancelled.

        Args:
            msg (PlanningActionResult): The message received from the /reaching_goal/result topic.
        """
        status = msg.status.status
        if status == 2:  # Goal cancelled (status = 2)
            self.TARGET_CANCELLED += 1
        elif status == 3:  # Goal reached (status = 3)
            self.TARGET_REACHED += 1

    def data(self, req):
        """
        The function that is called when the service is requested.

        Returns the response containing the current values of TARGET_CANCELLED and TARGET_REACHED.

        Args:
            req (goal_rc): The request message.

        Returns:
            goal_rcResponse: The response message.
        """
        return goal_rcResponse(self.TARGET_REACHED, self.TARGET_CANCELLED)


def main():
    """
    The main function that initializes the node and creates an instance of the Service class.
    """
    rospy.init_node('TARGETSERVICE')
    TARGETSERVICE = Service()
    pub = rospy.Publisher("my_turtle/cmd_vel", Twist)  # Publisher for the robot's velocity
    rospy.spin()


if __name__ == "__main__":
    main()


