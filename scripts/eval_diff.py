#still fine tuning it a bit will push soon
# To do : complete check_callback and report()
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
from geometry_msgs.msg import Pose
import time 
import math

class EvalDiff(Node):
    def __init__(self):
        super().__init__('eval_diff')
        self.position_sub_=self.create_subscription(Pose, '/model/my_robot/pose', self.position_callback, 10)
        self.target_sub_=self.create_subscription(Float64MultiArray, '/target',self.target_callback, 10)
        self.create_timer(0.01, self.check_callback) #check arrival and store metrics
        #Initialize variables
        self.current_x=None
        self.current_y=None
        self.start_x=None
        self.start_y=None
        self.target_x=None
        self.target_y=None
        self.start_time= 0.0
        self.elapsed = 0.0
        self.Accumulated_path_length=0
        self.last_x = None
        self.last_y = None
        self.idx = 0
        self.distance_idx=None


    def position_callback(self,msg):
        self.current_x= msg.position.x
        self.current_y= msg.position.y
        if self.last_x is None:
            self.last_x= self.current_x
            self.last_y= self.current_y
            return

        distance= math.hypot(self.current_x - self.last_x, self.current_y - self.last_y)

        self.Accumulated_path_length += distance

        self.last_x= self.current_x
        self.last_y= self.current_y
    
    def target_callback(self,msg):
        if self.target_x is None:
            start_x=self.current_x
            start_y=self.current_y
        elif self.target_x is not None:
            start_x=self.target_x
            start_y=self.target_x

            self.target_x = msg.data[0]
            self.target_y = msg.data[1]
            self.start_time = time.time()  # in target_callback when new target arrives
            self.idx +=1
            self.distance_idx=math.hypot(self.current_x - start_x , self.current_y - start_y)
            self.get_logger().info(f' Target no. {self.idx}: distance is {self.distance_idx:.2f}m')


    def report(self):
        if math.hypot(self.current_x - self.target_x , self.current_y - self.target_y):
            Reached = True
            if Reached == True:
                #can we use if Reached is not  False:
                self.elapsed = time.time() - self.start_time
                return
            
def main(args=None):  

    rclpy.init(args=args)
    node = EvalDiff()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()

        


        
        

