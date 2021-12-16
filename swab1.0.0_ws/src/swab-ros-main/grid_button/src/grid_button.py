#! /usr/bin/env python3
import time
import rospy
from std_msgs.msg import UInt8

def talker():
    pub = rospy.Publisher('grid_value', UInt8, queue_size=10)
    rospy.init_node('grid_button', anonymous=True)
    rate = rospy.Rate(10) # 10hz
    while not rospy.is_shutdown():
        print("grid? (g/n)\n")
        a = input()
        if (a=='g'): 
            print("start graph grid ......")
            msg = 1
            
            
            #msg = 0
            
            #print("joanne\n")
        else:
            msg = 0
            print("preparing grid ......")
            #print("nothing\n")
        

        #rospy.loginfo(msg)
        pub.publish(msg)	
        rate.sleep()

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass

