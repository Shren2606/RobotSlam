#!/usr/bin/env python3
import math
from enum import Enum
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Bool

class State(Enum):
    FREE = 0
    WARNING = 1
    DANGER = 2


class SafetyStop(Node):

    def __init__(self):
        super().__init__("safety_stop_node")
        self.declare_parameter("danger_distance", 0.8)
        self.declare_parameter("scan_topic", "scan")
        self.declare_parameter("safety_stop_topic", "safety_stop")

        self.danger_distance=self.get_parameter("danger_distance").get_parameter_value().double_value
        self.scan_topic =self.get_parameter("scan_topic").get_parameter_value().string_value
        self.safety_stop_topic =self.get_parameter("safety_stop_topic").get_parameter_value().string_value

        self.laser_sub = self.create_subscription(LaserScan,self.scan_topic, self.laser_callback, 10)
        self.safety_stop_pub = self.create_publisher(Bool, self.safety_stop_topic, 10)

        self.state = State.FREE

    def laser_callback(self, msg: LaserScan):
        self.state = State.FREE

        for range_value in msg.ranges:
            if math.isfinite(range_value):
                self.get_logger().info(
                    f"Range value: {range_value:.3f} m"
                )
                if range_value <= self.danger_distance:
                    self.state = State.DANGER
                    break
        is_safety_stop = Bool()
        if self.state == State.DANGER:
            is_safety_stop.data = True
        elif self.state == State.FREE:
            is_safety_stop.data = False

        self.safety_stop_pub.publish(is_safety_stop)



def main():

    # Initialize ROS 2
    rclpy.init()

    # Create TwistRelayNode node
    node = SafetyStop()

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

