#!/usr/bin/env python3
import sys
import termios
import tty
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class WASDTeleop(Node):
    def __init__(self):
        super().__init__('wasd_teleop')
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.linear_speed = 0.3
        self.angular_speed = 0.8
        self.strafe_speed = 0.3

    def get_key(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            key = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return key

    def run(self):
        print("WASD to move, Q/E to strafe left/right, X to stop, Ctrl+C to quit")
        twist = Twist()
        while rclpy.ok():
            key = self.get_key()
            twist = Twist()
            if key == 'w':
                twist.linear.x = self.linear_speed
            elif key == 's':
                twist.linear.x = -self.linear_speed
            elif key == 'a':
                twist.angular.z = self.angular_speed
            elif key == 'd':
                twist.angular.z = -self.angular_speed
            elif key == 'q':
                twist.linear.y = self.strafe_speed
            elif key == 'e':
                twist.linear.y = -self.strafe_speed
            elif key == 'x':
                pass
            elif key == '\x03':
                break
            self.pub.publish(twist)

def main():
    rclpy.init()
    node = WASDTeleop()
    try:
        node.run()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()