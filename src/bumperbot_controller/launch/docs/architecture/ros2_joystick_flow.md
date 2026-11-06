# ROS 2 Joystick Control Architecture

```mermaid
flowchart TD
    A["USB Joystick / Gamepad"] --> B["joy_linux_node"]
    B --> C["ROS 2 Topic: /joy"]
    C --> D["joy_teleop"]
    D --> E["ROS 2 Topic: /cmd_vel"]
    E --> F["SimpleController / DiffDriveController"]
    F --> G["Robot Wheels"]
```