#! /usr/bin/env python3

# This file Subscribe '/button_value' '/sticks' '/tof_data'
# construct cmd by sticks and publish to '/joy_information'
# if button be pressed will send a series of cmd by time.sleep to execute 
# swabbing process


import rospy
from std_msgs.msg import String, UInt16, UInt8
import os
import json
import time

button_value = 0
swab_status = 0

HZ=10
tofd = 0

stepAngle = 1.8
pulse_per_sec = 160 
lead = 2
dis_per_sec = stepAngle * pulse_per_sec * lead / 360
'''
def callback1(data):
    global tofd
    tofd = data.data
    if tofd > 150 or tofd < 90:
        tofd = 100
'''
def button_callback(msg):
    global button_value, dis_per_sec 
    button_value = msg.data
    up=down=left=right=front=behind=spin=rcm_en=ee_en=STOP=0
    
    #print(pub_status)
    if button_value ==2:
            
        front=1
        cmd = "%05d*%05d*%03d*%03d*%01d*%01d*%01d*%01d*%01d*%01d*%021d" % (0,0,0,0,front,behind,spin,rcm_en,ee_en,STOP,0)        
        swab_status = 1
        pub_joy.publish(cmd)
        pub_status.publish(swab_status)
        print(cmd)

        time.sleep(1)

        front=0
        swab_status = 2
        cmd = "%05d*%05d*%03d*%03d*%01d*%01d*%01d*%01d*%01d*%01d*%021d" % (0,0,0,0,front,behind,spin,rcm_en,ee_en,STOP,0)        
        pub_joy.publish(cmd)
        pub_status.publish(swab_status)
        print(cmd)
        '''
        time.sleep(1)
        
        ee_en=1
        spin = 2000
        swab_status = 1
        cmd = "%05d*%05d*%03d*%03d*%01d*%01d*%01d*%01d*%01d*%01d*%021d" % (0,0,0,0,front,behind,spin,rcm_en,ee_en,STOP,0)        
        pub_joy.publish(cmd)
        pub_status.publish(swab_status)
        print(cmd)

  
        time.sleep(3)

        ee_en=0
        spin=0
        cmd = "%05d*%05d*%03d*%03d*%01d*%01d*%01d*%01d*%01d*%01d*%021d" % (0,0,0,0,front,behind,spin,rcm_en,ee_en,STOP,0)        
        pub_joy.publish(cmd)
        pub_status.publish(swab_status)
        print(cmd)

        time.sleep(1)
        
        behind=1000
        cmd = "%05d*%05d*%03d*%03d*%01d*%01d*%01d*%01d*%01d*%01d*%021d" % (0,0,0,0,front,behind,spin,rcm_en,ee_en,STOP,0)        
        pub_joy.publish(cmd)
        pub_status.publish(swab_status)
        print(cmd)
        time.sleep(6)

        behind=0
        cmd = "%05d*%05d*%03d*%03d*%01d*%01d*%01d*%01d*%01d*%01d*%021d" % (0,0,0,0,front,behind,spin,rcm_en,ee_en,STOP,0)        
        swab_status = 0
        pub_joy.publish(cmd)
        pub_status.publish(swab_status)
        print(cmd)
        '''
        print("swab end ... ... \n")
        print("swab start? (y/n)\n")
        time.sleep(1)
        swab_status = 3
        pub_status.publish(swab_status)
        
    elif button_value == 0:
        up=down=left=right=front=behind=spin=rcm_en=ee_en=STOP=0
        cmd = "%05d*%05d*%03d*%03d*%01d*%01d*%01d*%01d*%01d*%01d*%021d" % (0,0,0,0,front,behind,spin,rcm_en,ee_en,STOP,0)      
        swab_status = 0
        pub_joy.publish(cmd)
        pub_status.publish(swab_status)
        print(cmd)




def sticks_remapping(msg):
    global button_value
    up=down=left=right=front=behind=spin=rcm_en=ee_en=STOP=0
    rate = rospy.Rate(HZ)
    if button_value == 0:
        cmd = "%05d*%05d*%03d*%03d*%01d*%01d*%01d*%01d*%01d*%01d*%021d" % (0,0,0,0,front,behind,spin,rcm_en,ee_en,STOP,0)      
        pub_joy.publish(cmd)
    rate.sleep()


 
if __name__ == '__main__':
    rospy.init_node('panel_info_process')
    
    pub_joy = rospy.Publisher('joy_information', String, queue_size=1)
    pub_status = rospy.Publisher('swab_status', UInt8, queue_size=1)

    rospy.Subscriber('swab_button_ui', UInt8, button_callback, queue_size = 1, buff_size = 52428800)
    rospy.spin()
