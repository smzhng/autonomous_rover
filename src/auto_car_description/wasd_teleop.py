#!/usr/bin/env python3
import sys
import termios
import tty
import select
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class WASDTeleop(Node):
    def __init__(self):
        super().__init__('wasd_teleop')
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.linear_speed = 1.0
        self.angular_speed = 2.5
        self.linear_x = 0.0
        self.angular_z = 0.0

    def get_key(self, timeout=0.1):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            rlist, _, _ = select.select([sys.stdin], [], [], timeout)
            if rlist:
                key = sys.stdin.read(1)
            else:
                key = ''
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return key

    def run(self):
        print("W/S = forward/back, A/D = rotate left/right, hold combos to curve, X = stop, Ctrl+C = quit")
        while rclpy.ok():
            key = self.get_key()

            if key == 'w':
                self.linear_x = self.linear_speed
            elif key == 's':
                self.linear_x = -self.linear_speed
            elif key == 'a':
                self.angular_z = self.angular_speed
            elif key == 'd':
                self.angular_z = -self.angular_speed
            elif key == 'x':
                self.linear_x = 0.0
                self.angular_z = 0.0
            elif key == '\x03':
                break
            elif key == '':
                # No key pressed recently, decay to stop
                self.linear_x = 0.0
                self.angular_z = 0.0

            twist = Twist()
            twist.linear.x = self.linear_x
            twist.angular.z = self.angular_z
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