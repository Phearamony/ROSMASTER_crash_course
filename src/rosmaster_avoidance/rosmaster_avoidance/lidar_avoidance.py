"""LiDAR obstacle avoidance for the ROSMASTER A1 (Week 1).

Reads the LiDAR scan on /scan and publishes driving commands on /cmd_vel.
The same node works in Gazebo and on the real robot, because both use
the same two topics.

Rules:
  1. Front is clear        -> drive forward
  2. Front is blocked      -> slow down and steer toward the side with more space
  3. Something is too close -> back up for a moment, steering the other way
"""
import math

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist


class LidarAvoidance(Node):

    def __init__(self):
        super().__init__('lidar_avoidance')

        # Parameters you can change from the terminal with -p name:=value
        self.declare_parameter('forward_speed', 0.25)   # m/s
        self.declare_parameter('turn_speed', 1.0)       # rad/s
        self.declare_parameter('safe_distance', 0.7)    # m, start turning
        self.declare_parameter('stop_distance', 0.3)    # m, back up

        self.scan_sub = self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        self.backup_ticks = 0   # how many more scans to keep backing up
        self.backup_turn = 0.0
        self.get_logger().info('LiDAR avoidance started. Waiting for /scan ...')

    def sector_min(self, scan, start_deg, end_deg):
        """Closest distance seen between two angles (0 = front, + = left)."""
        closest = float('inf')
        for i, r in enumerate(scan.ranges):
            angle = math.degrees(scan.angle_min + i * scan.angle_increment)
            angle = (angle + 180.0) % 360.0 - 180.0   # wrap to -180..180
            if start_deg <= angle <= end_deg and scan.range_min < r < scan.range_max:
                closest = min(closest, r)
        return closest

    def scan_callback(self, scan):
        forward_speed = self.get_parameter('forward_speed').value
        turn_speed = self.get_parameter('turn_speed').value
        safe = self.get_parameter('safe_distance').value
        stop = self.get_parameter('stop_distance').value

        front = self.sector_min(scan, -25, 25)
        left = self.sector_min(scan, 25, 90)
        right = self.sector_min(scan, -90, -25)

        cmd = Twist()

        if self.backup_ticks > 0:
            # Rule 3 (continued): keep reversing for a short time
            self.backup_ticks -= 1
            cmd.linear.x = -0.15
            cmd.angular.z = self.backup_turn
            state = 'BACKING UP'
        elif front < stop:
            # Rule 3: too close, start backing up (about 1.5 s at 10 Hz)
            self.backup_ticks = 15
            # Reversing with the wheels turned swings the nose toward that side,
            # so steer toward the side that has more space
            self.backup_turn = turn_speed if left > right else -turn_speed
            cmd.linear.x = -0.15
            cmd.angular.z = self.backup_turn
            state = 'TOO CLOSE'
        elif front < safe:
            # Rule 2: obstacle ahead, turn toward the more open side
            cmd.linear.x = forward_speed * 0.6
            cmd.angular.z = turn_speed if left > right else -turn_speed
            state = 'TURN LEFT' if cmd.angular.z > 0 else 'TURN RIGHT'
        else:
            # Rule 1: path is clear, go forward and keep away from side walls
            cmd.linear.x = forward_speed
            if min(left, right) < safe * 0.6:
                cmd.angular.z = 0.4 * turn_speed if left > right else -0.4 * turn_speed
            state = 'FORWARD'

        self.cmd_pub.publish(cmd)
        self.get_logger().info(
            f'{state:<10} front={front:4.2f} left={left:4.2f} right={right:4.2f}',
            throttle_duration_sec=0.5)

    def stop_robot(self):
        self.cmd_pub.publish(Twist())


def main():
    rclpy.init()
    node = LidarAvoidance()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.stop_robot()
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
