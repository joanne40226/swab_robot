#! /usr/bin/env python3
import time

from numpy.core.numeric import True_
import rospy
from std_msgs.msg import UInt8

def talker():
    pub = rospy.Publisher('swab_button_value', UInt8, queue_size=10)
    rospy.init_node('swab_button', anonymous=True)
    rate = rospy.Rate(10) # 10hz
    first = True_
    while not rospy.is_shutdown():
        print("swab start? (y/n)\n")
        msg = 0
        a = input()
        
        if (a=='y'): 
            #print("start swabbing ......")
            msg = 1
            
            
            #msg = 0
            
            #print("joanne\n")
        else:
            msg = 0
            #print("preparing ......")
            #print("nothing\n")
        

        #rospy.loginfo(msg)
        pub.publish(msg)	
        rate.sleep()

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass
