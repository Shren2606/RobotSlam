#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

class SafetyStop(Node):

    def __init__(self):
        super().__init__("safety_stop_node")
        self.declare_parameter("danger_distance", 0.2)
