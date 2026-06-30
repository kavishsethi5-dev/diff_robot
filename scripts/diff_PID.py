#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from std_msgs.msg import Float64MultiArray
from geometry_msgs.msg import Pose
import math

class diff_PID(Node):

    def __init__(self):
        super().__init__('diff_PID')
        self.create_subscription(Pose, '/model/my_robot/pose', self.odom_callback, 10)
        self.subscriber_target_=self.create_subscription( Float64MultiArray, '/target', self.target_callback, 10)
        self.publishers_cmd_vel_=self.create_publisher(Twist, '/cmd_vel', 10)
        self.target_x=0.0 #empty value 
        self.target_y=0.0

        # Defined once in __init__
        self.kp = 1.2
        self.ki= 0.01
        self.kd = 0.05
        #Decided to add angular kp,ki,kd values also (will add reason later )
        self.kp_a = 4.0
        self.ki_a = 0.01
        self.kd_a = 0.05 #assuming similar values
        
        ####Initializing variables####
        self.last_error = 0.0
        self.error_sum = 0.0
         #  Extract Current Position (X, Y)
        self.x_current = 0.0
        self.y_current = 0.0

        # 2. Extract and Calculate Current Heading (Theta)
        self.qx = 0.0
        self.qy = 0.0
        self.qz = 0.0
        self.qw = 0.0
        # similar variables for angular
        self.last_error_a = 0.0
        self.error_sum_a = 0.0
        

        


        #for now setting dt as 0.01, later I can see it in gazebo physics
        self.target_x = None
        self.target_y = None


        #create timer
        time_period=0.01
        self.timer = self.create_timer( time_period , self.PID_callback)

    def PID_callback(self):

        # Safety
        if self.target_x is None:
            return 
       
        siny_cosp = 2 * (self.qw * self.qz + self.qx * self.qy)
        cosy_cosp = 1 - 2 * (self.qy * self.qy + self.qz * self.qz)
        theta_current = math.atan2(siny_cosp, cosy_cosp)

        # Math Formula 1: Distance Error 
        distance_error = math.sqrt((self.target_x - self.x_current)**2 + (self.target_y - self.y_current)**2)
        self.current_error = distance_error
        
        # Math Formula 2: Desired Heading Angle (Alpha)

        alpha = math.atan2(self.target_y - self.y_current, self.target_x - self.x_current)
        
        # Math Formula 3: Angular Error
        angle_error = alpha - theta_current
        angle_error = math.atan2(math.sin(angle_error), math.cos(angle_error))
        #Normalize angle_error to stay within [-pi, pi] eg 90 vs -270
        # defining self current error first
        self.current_error_a = angle_error


        self.get_logger().info(
            f"Target: ({self.target_x}, {self.target_y}) | "
            f"Dist : {distance_error:.2f}m | "
            f"Ang: {math.degrees(angle_error):.1f}°")
        #tp
        time_step=0.01
        #now using the calc to get PID
        P = self.kp * self.current_error
        I = self.ki * self.error_sum
        self.error_sum += self.current_error * time_step
        error_change = (self.current_error - self.last_error) / time_step
        D = self.kd * error_change

        #PID calc for angular
        P_a = self.kp_a * self.current_error_a
        self.error_sum_a += self.current_error_a * time_step
        I_a = self.ki_a * self.error_sum_a
        error_change_a = (self.current_error_a - self.last_error_a) / time_step
        D_a = self.kd_a * error_change_a


        #updating the last value
        self.last_error = self.current_error
        self.last_error_a = self.current_error_a
        


        #final
        pid_dist = min(P + I + D, 1.0)  
        pid_angle = max(-2.0, min(2.0, P_a + I_a + D_a))


        if distance_error < 0.15:  #this was done to stop it from circling at the end
            fmsg = Twist()   # zero velocity
            self.publishers_cmd_vel_.publish(fmsg)
            return           # exits PID_callback right here
        
        
        fmsg = Twist()
        heading_factor = max(0.0, math.cos(angle_error)) # cos angle error or cos pid_angle?
        # this is to stop the spinning (also tuning ka_a)
        fmsg.linear.x =  pid_dist* heading_factor  # drives at ~0 at 163°, full speed when aligned
        fmsg.angular.z = pid_angle


        #publish this message to cmd_vel
        self.publishers_cmd_vel_.publish(fmsg)

        
        




        

      
    def odom_callback(self, msg):# 1. Extract the raw 4D Quaternion fields
        self.x_current = msg.position.x      # was msg.pose.pose.position.x
        self.y_current = msg.position.y
        self.qx = msg.orientation.x          # was msg.pose.pose.orientation.x
        self.qy = msg.orientation.y
        self.qz = msg.orientation.z
        self.qw = msg.orientation.w

    

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
    node = diff_PID()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()

    