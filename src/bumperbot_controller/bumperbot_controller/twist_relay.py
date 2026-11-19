#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, TwistStamped

class TwistRelay(Node):
    def __init__(self):
        # Initialize the ROS 2 node
        super().__init__("twist_relay")
        self.controler_sub = self.create_subscription(
            Twist,
            "/bumperbot_controller/cmd_vel_unstamped",
            self.controller_twist_callback,
            10
        )

        self.controler_pub = self.create_publisher(
            TwistStamped,
            "/bumperbot_controller/cmd_vel",
            10
        )

        self.joy_sub = self.create_subscription(
            Twist,
            "/input_joy/cmd_vel_unstamped",
            self.joy_twist_callback,
            10
        )

        self.joy_pub = self.create_publisher(
            TwistStamped,
            "/input_joy/cmd_vel",
            10
        )

    def controller_twist_callback(self, msg):
        twist_stamped = TwistStamped()
        twist_stamped.header.stamp = self.get_clock().now().to_msg()
        twist_stamped.twist = msg
        self.controler_pub.publish(twist_stamped)

    def joy_twist_callback(self, msg):
        twist = Twist
        twist = msg.twist
        self.joy_pub.publish(twist)

def main():

    # Initialize ROS 2
    rclpy.init()

    # Create TwistRelay node
    node = TwistRelay()

    # Keep the node running and process callbacks
    rclpy.spin(node)

    # Destroy the node after spinning
    node.destroy_node()

    # Shutdown ROS 2
    rclpy.shutdown()


# ============================================================
# PYTHON ENTRY POINT
# ============================================================

# Execute main() only when this file is run directly
if __name__ == '__main__':
    main()

