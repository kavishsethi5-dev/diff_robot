#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from std_msgs.msg import Float64MultiArray
import math

class DiffController(Node):

    def __init__(self):
        super().__init__('diff_controller')
        self.subscriber_odom_=self.create_subscription(Odometry, '/odom', self.odom_callback, 10)
        self.subscriber_target_=self.create_subscription( Float64MultiArray, '/target', self.target_callback, 10)
        self.publishers_cmd_vel_=self.create_publisher(Twist, '/cmd_vel', 10)
        self.target_x=0.0 #empty value 
        self.target_y=0.0

      
    def odom_callback(self, msg):# 1. Extract the raw 4D Quaternion fields
        # 1. Extract Current Position (X, Y)
        x_current = msg.pose.pose.position.x
        y_current = msg.pose.pose.position.y
        # 2. Extract and Calculate Current Heading (Theta)
        qx = msg.pose.pose.orientation.x
        qy = msg.pose.pose.orientation.y
        qz = msg.pose.pose.orientation.z
        qw = msg.pose.pose.orientation.w
        
        siny_cosp = 2 * (qw * qz + qx * qy)
        cosy_cosp = 1 - 2 * (qy * qy + qz * qz)
        theta_current = math.atan2(siny_cosp, cosy_cosp)
        # Math Formula 1: Distance Error (Pythagorean theorem)
        distance_error = math.sqrt((self.target_x - x_current)**2 + (self.target_y - y_current)**2)
        
        # Math Formula 2: Desired Heading Angle (Alpha)
        alpha = math.atan2(self.target_y - y_current, self.target_x - x_current)
        
        # Math Formula 3: Angular Error
        angle_error = alpha - theta_current
        angle_error = math.atan2(math.sin(angle_error), math.cos(angle_error))
        #Normalize angle_error to stay within [-pi, pi] eg 90 vs -270
        self.get_logger().info(
            f"Target: ({self.target_x}, {self.target_y}) | "
            f"Dist : {distance_error:.2f}m | "
            f"Ang: {math.degrees(angle_error):.1f}°"
        )


        fmsg = Twist()
        fmsg.linear.x =  distance_error/ 5.0
        fmsg.angular.z = angle_error/ 5.0


        #publish this message to cmd_vel
        self.publishers_cmd_vel_.publish(fmsg)



    

    def target_callback(self, FMAmsg):
        #FMAmsg = Float64MultiArray() # with this we can specify the target position
        # also PoseStamped can be used for this purpose
        #FMAmsg.data = [5.0, 5.0, 0.0]
        #self.subscriber_odom_.publish(FMAmsg)
         #all this is not needed if we are getting this FMAmsg from a terminal or another node
        self.target_x = FMAmsg.data[0]
        self.target_y = FMAmsg.data[1]





def main(args=None):  

    rclpy.init(args=args)
    diff_controller = DiffController()
    rclpy.spin(diff_controller)
    rclpy.shutdown()

if __name__ == '__main__':
    main()