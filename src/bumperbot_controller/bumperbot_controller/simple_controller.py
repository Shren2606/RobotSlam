#!/usr/bin/env python3

# ============================================================
# IMPORT LIBRARIES
# ============================================================

import rclpy
from rclpy.node import Node

# Convert seconds to nanoseconds
from rclpy.constants import S_TO_NS

# ROS 2 time utilities
from rclpy.time import Time

# Standard ROS 2 messages
from std_msgs.msg import Float64MultiArray
from geometry_msgs.msg import TwistStamped
from sensor_msgs.msg import JointState
from nav_msgs.msg import Odometry

# Numerical computation library
import numpy as np

# TF broadcaster for publishing coordinate transforms
from tf2_ros import TransformBroadcaster
from geometry_msgs.msg import TransformStamped

# Mathematical functions
import math

# Convert Euler angles into quaternion
from tf_transformations import quaternion_from_euler


# ============================================================
# SIMPLE CONTROLLER NODE
# ============================================================

class SimpleController(Node):

    def __init__(self):
        # Initialize the ROS 2 node
        super().__init__("simple_controller")

        # ----------------------------------------------------
        # DECLARE PARAMETERS
        # ----------------------------------------------------

        # Declare the wheel radius parameter in meters
        self.declare_parameter("wheel_radius", 0.033)

        # Declare the distance between two wheels in meters
        self.declare_parameter("wheel_separation", 0.17)

        # Read wheel radius from ROS 2 parameters
        self.wheel_radius_ = self.get_parameter(
            "wheel_radius"
        ).get_parameter_value().double_value

        # Read wheel separation from ROS 2 parameters
        self.wheel_separation_ = self.get_parameter(
            "wheel_separation"
        ).get_parameter_value().double_value

        # Display wheel parameters in the terminal
        self.get_logger().info(
            "Using wheel radius %f" % self.wheel_radius_
        )

        self.get_logger().info(
            "Using wheel separation %f" % self.wheel_separation_
        )

        # ----------------------------------------------------
        # INITIALIZE ROBOT STATE
        # ----------------------------------------------------

        # Previous left wheel position in radians
        self.left_wheel_prev_pos_ = 0.0

        # Previous right wheel position in radians
        self.right_wheel_prev_pos_ = 0.0

        # Robot position in the odom coordinate frame
        self.x_ = 0.0
        self.y_ = 0.0

        # Robot orientation around the Z axis
        self.theta_ = 0.0

        # ----------------------------------------------------
        # ROS 2 PUBLISHERS AND SUBSCRIBERS
        # ----------------------------------------------------

        # Publisher for wheel angular velocity commands
        self.wheel_cmd_pub_ = self.create_publisher(
            Float64MultiArray,
            "simple_velocity_controller/commands",
            10
        )

        # Subscribe to robot velocity commands
        self.vel_sub_ = self.create_subscription(
            TwistStamped,
            "bumperbot_controller/cmd_vel",
            self.velCallback,
            10
        )

        # Subscribe to wheel joint states
        self.joint_sub_ = self.create_subscription(
            JointState,
            "joint_states",
            self.jointCallback,
            10
        )

        # Publisher for robot odometry
        self.odom_pub_ = self.create_publisher(
            Odometry,
            "bumperbot_controller/odom",
            10
        )

        # ----------------------------------------------------
        # DIFFERENTIAL DRIVE SPEED CONVERSION MATRIX
        # ----------------------------------------------------

        # Convert robot linear/angular velocity into
        # left and right wheel angular velocities
        #
        # [ v ]   [ r/2       r/2      ] [ w_right ]
        # [ w ] = [ r/L      -r/L      ] [ w_left  ]
        #
        # r = wheel radius
        # L = wheel separation

        self.speed_conversion_ = np.array([
            [
                self.wheel_radius_ / 2,
                self.wheel_radius_ / 2
            ],
            [
                self.wheel_radius_ / self.wheel_separation_,
                -self.wheel_radius_ / self.wheel_separation_
            ]
        ])

        # Display the conversion matrix
        self.get_logger().info(
            "The conversion matrix is %s"
            % self.speed_conversion_
        )

        # ----------------------------------------------------
        # INITIALIZE ODOMETRY MESSAGE
        # ----------------------------------------------------

        # Create an Odometry message
        self.odom_msg_ = Odometry()

        # Set the reference coordinate frame
        self.odom_msg_.header.frame_id = "odom"

        # Set the robot base coordinate frame
        self.odom_msg_.child_frame_id = "base_footprint"

        # Initialize robot orientation to identity quaternion
        self.odom_msg_.pose.pose.orientation.x = 0.0
        self.odom_msg_.pose.pose.orientation.y = 0.0
        self.odom_msg_.pose.pose.orientation.z = 0.0
        self.odom_msg_.pose.pose.orientation.w = 1.0

        # ----------------------------------------------------
        # INITIALIZE TF BROADCASTER
        # ----------------------------------------------------

        # Create a TF broadcaster
        self.br_ = TransformBroadcaster(self)

        # Create a TransformStamped message
        self.transform_stamped_ = TransformStamped()

        # Parent coordinate frame
        self.transform_stamped_.header.frame_id = "odom"

        # Child coordinate frame
        self.transform_stamped_.child_frame_id = "base_footprint"

        # ----------------------------------------------------
        # INITIALIZE TIME
        # ----------------------------------------------------

        # Store the current ROS time
        self.prev_time_ = self.get_clock().now()


    # ========================================================
    # VELOCITY CALLBACK
    # ========================================================

    def velCallback(self, msg):

        # ----------------------------------------------------
        # DIFFERENTIAL DRIVE INVERSE KINEMATICS
        # ----------------------------------------------------

        # Extract robot linear and angular velocity
        #
        # robot_speed = [ linear velocity ]
        #                [ angular velocity ]

        robot_speed = np.array([
            [msg.twist.linear.x],
            [msg.twist.angular.z]
        ])

        # Calculate the inverse of the conversion matrix
        # to obtain wheel angular velocities
        wheel_speed = np.matmul(
            np.linalg.inv(self.speed_conversion_),
            robot_speed
        )

        # ----------------------------------------------------
        # CREATE WHEEL COMMAND MESSAGE
        # ----------------------------------------------------

        # Create a Float64MultiArray message
        wheel_speed_msg = Float64MultiArray()

        # Store wheel angular velocities
        # The order is right wheel first, left wheel second
        wheel_speed_msg.data = [
            wheel_speed[1, 0],
            wheel_speed[0, 0]
        ]

        # Publish wheel velocity commands
        self.wheel_cmd_pub_.publish(wheel_speed_msg)


    # ========================================================
    # JOINT STATE CALLBACK
    # ========================================================

    def jointCallback(self, msg):

        # ----------------------------------------------------
        # CALCULATE WHEEL POSITION INCREMENTS
        # ----------------------------------------------------

        # Calculate the change in left wheel position
        dp_left = (
            msg.position[1]
            - self.left_wheel_prev_pos_
        )

        # Calculate the change in right wheel position
        dp_right = (
            msg.position[0]
            - self.right_wheel_prev_pos_
        )

        # Calculate elapsed time between two joint updates
        dt = Time.from_msg(msg.header.stamp) - self.prev_time_

        # ----------------------------------------------------
        # UPDATE PREVIOUS WHEEL POSITIONS AND TIME
        # ----------------------------------------------------

        # Store current left wheel position
        self.left_wheel_prev_pos_ = msg.position[1]

        # Store current right wheel position
        self.right_wheel_prev_pos_ = msg.position[0]

        # Store current timestamp
        self.prev_time_ = Time.from_msg(msg.header.stamp)

        # ----------------------------------------------------
        # CALCULATE WHEEL ANGULAR VELOCITIES
        # ----------------------------------------------------

        # Convert wheel position increments into angular velocity
        # dt.nanoseconds / S_TO_NS converts nanoseconds to seconds

        fi_left = dp_left / (
            dt.nanoseconds / S_TO_NS
        )

        fi_right = dp_right / (
            dt.nanoseconds / S_TO_NS
        )

        # ----------------------------------------------------
        # CALCULATE ROBOT VELOCITIES
        # ----------------------------------------------------

        # Calculate robot linear velocity
        #
        # v = r * (w_right + w_left) / 2

        linear = (
            self.wheel_radius_ * fi_right
            + self.wheel_radius_ * fi_left
        ) / 2

        # Calculate robot angular velocity
        #
        # w = r * (w_right - w_left) / L

        angular = (
            self.wheel_radius_ * fi_right
            - self.wheel_radius_ * fi_left
        ) / self.wheel_separation_

        # ----------------------------------------------------
        # CALCULATE ROBOT POSITION INCREMENTS
        # ----------------------------------------------------

        # Calculate the distance traveled by the robot
        d_s = (
            self.wheel_radius_ * dp_right
            + self.wheel_radius_ * dp_left
        ) / 2

        # Calculate the change in robot orientation
        d_theta = (
            self.wheel_radius_ * dp_right
            - self.wheel_radius_ * dp_left
        ) / self.wheel_separation_

        # Update robot orientation
        self.theta_ += d_theta

        # Update robot X position in the odom frame
        self.x_ += d_s * math.cos(self.theta_)

        # Update robot Y position in the odom frame
        self.y_ += d_s * math.sin(self.theta_)

        # ----------------------------------------------------
        # CONVERT ROBOT ORIENTATION TO QUATERNION
        # ----------------------------------------------------

        # Convert yaw angle into quaternion representation
        q = quaternion_from_euler(0, 0, self.theta_ )

        # ----------------------------------------------------
        # UPDATE ODOMETRY MESSAGE
        # ----------------------------------------------------

        # Set odometry timestamp
        self.odom_msg_.header.stamp = (
            self.get_clock().now().to_msg()
        )

        # Update robot position
        self.odom_msg_.pose.pose.position.x = self.x_
        self.odom_msg_.pose.pose.position.y = self.y_

        # Update robot orientation
        self.odom_msg_.pose.pose.orientation.x = q[0]
        self.odom_msg_.pose.pose.orientation.y = q[1]
        self.odom_msg_.pose.pose.orientation.z = q[2]
        self.odom_msg_.pose.pose.orientation.w = q[3]

        # Update robot linear velocity
        self.odom_msg_.twist.twist.linear.x = linear

        # Update robot angular velocity
        self.odom_msg_.twist.twist.angular.z = angular

        # Publish odometry information
        self.odom_pub_.publish(self.odom_msg_)

        # ----------------------------------------------------
        # PUBLISH TF: ODOM -> BASE_FOOTPRINT
        # ----------------------------------------------------

        # Update robot translation
        self.transform_stamped_.transform.translation.x = self.x_
        self.transform_stamped_.transform.translation.y = self.y_

        # Update robot rotation
        self.transform_stamped_.transform.rotation.x = q[0]
        self.transform_stamped_.transform.rotation.y = q[1]
        self.transform_stamped_.transform.rotation.z = q[2]
        self.transform_stamped_.transform.rotation.w = q[3]

        # Update TF timestamp
        self.transform_stamped_.header.stamp = (
            self.get_clock().now().to_msg()
        )

        # Broadcast the transform to the ROS 2 TF system
        self.br_.sendTransform(self.transform_stamped_)


# ============================================================
# MAIN FUNCTION
# ============================================================

def main():

    # Initialize ROS 2
    rclpy.init()

    # Create SimpleController node
    simple_controller = SimpleController()

    # Keep the node running and process callbacks
    rclpy.spin(simple_controller)

    # Destroy the node after spinning
    simple_controller.destroy_node()

    # Shutdown ROS 2
    rclpy.shutdown()


# ============================================================
# PYTHON ENTRY POINT
# ============================================================

# Execute main() only when this file is run directly
if __name__ == '__main__':
    main()
