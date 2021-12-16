#!/usr/bin/env python3
""" 
-------------------------
Author : Jing-Shiang Wuu, Li-Wei Yang
Date : 2021/7/1
Institution : National Taiwan University 
Department : Bio-Mechatronics Engineering
Status : Senior, Junior
-------------------------

Description:
    It is a program to recieve all the sensor informatoin, including tof(may be deleted), limit switch, button, sticks and image. 
    we plot some important information on the image:
    1. swabing target: there is a tip_offset from the center of image
    2. swabing status: showing the swabing status:searching, swabing in the lower right corner of image
    3. warning information: if the robot touch the limit switch, there is a warning information in the lower right corner of image too.
    the image will zoom in/out if
        * dataz > 21500 ---> zoom in
        * dataz < 18500 ---> zoom out
    the maximum magnification is 10
"""
from __future__ import print_function
import os
import time
import sys
import rospy
import cv2
import numpy as np

from cv_bridge import CvBridge, CvBridgeError
from rospy.timer import sleep
from std_msgs.msg import String, UInt16, UInt8
from sensor_msgs.msg import Image

import time

datax = " "
datay = " "
dataz = 0
tofd = 0
scale = 1.0 # magnification >1 , <=100 , step = 0.1
grid = 0

mode = 0
switch_state = "0000"  #down,up,right,left
swab_state = 0

swab_button_ui = 0
grid_record = 0
draw_x1 = 0
draw_y1 = 0
draw_x2= 0
draw_y2 = 0
mouseX = float(0)
mouseY = float(0)
mouseXD = float(0)
mouseYD = float(0)
pic_count = 0
state = 1

screen_shot_ban = 0
ui_ban = 0
screen_shot_gogogo = 0
swab_position_count = 0
record_1 = 0
shot_1 = 0
record_2 = 0
shot_2 = 0

state_1_ban = 0
state_2_ban = 1
state_3_ban = 1

chang_state = 0
swab_b = 0

a=0

def init_canvas(width, height, color=(255, 255, 255)):
    canvas = np.ones((height, width, 3), dtype="uint8")

    # 将原来的三个通道抽离出来， 分别乘上各个通道的值
    (channel_b, channel_g, channel_r) = cv2.split(canvas)
    # 颜色的值与个通道的全1矩阵相乘
    channel_b *= color[0]
    channel_g *= color[1]
    channel_r *= color[2]

    # cv.merge 合并三个通道的值
    return cv2.merge([channel_b, channel_g, channel_r])
class image_converter:

    def __init__(self):
        # self.image_pub = rospy.Publisher("image_topic_2",Image,queue_size=10)
        self.bridge = CvBridge()
        self.image_sub = rospy.Subscriber("/usb_cam/image_raw",Image,self.callback)
        self.pub_lt = rospy.Publisher("swab_button_ui", UInt8, queue_size=10)
        #rospy.Subscriber("sticks", Sticks, stick_callback) #String or Sticks
        #rospy.Subscriber("tof_data", UInt16, tof_callback) #String or Sticks
        #rospy.Subscriber('swab_button_value', UInt8, button_callback)
        #rospy.Subscriber('limit_switch_state', String, limit_switch_callback)
        rospy.Subscriber("swab_status",UInt8,swab_state_callback)
        #self.old_tofd = 0
    def callback(self,data):
        global scale, mode,  swab_state
        global dataz
        global grid_record
        global mouseX,mouseY
        global pic_count
        global screen_shot_gogogo
        global swab_position_count
        global draw_x1,draw_x2
        global draw_y1,draw_y2
        global state
        global record_1
        global shot_1   
        global record_2
        global shot_2 
        global state_1_ban
        global state_2_ban
        global chang_state  
        global state_3_ban
        global mouseXD,mouseYD
        global swab_b
        global a

        try:
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
            #print("try")
        except CvBridgeError as e:
            print("error!")

        tip_woffset = 0

        L = 114.83
        h = 480
        d = 16.17
        beta = 0.823

        

        x = h/2 -((L-(d/np.tan(beta/2)))/L)*(h/2)
        tip_hoffset = int(x)       

        width = cv_image.shape[1]
        height = cv_image.shape[0]
        # zoom in & out based on target center 
        centerX,centerY=int(height/2+tip_hoffset),int(width/2)
        # set coordinates
        
        radiusX_up = int((1/scale)*(0.5*height+tip_hoffset))
        radiusX_down = int((1/scale)*(0.5*height-tip_hoffset))
        radiusY = int((1/scale)*(0.5*width))
        minX,maxX=centerX-radiusX_up,centerX+radiusX_down
        minY,maxY=centerY-radiusY,centerY+radiusY

        cropped = cv_image[minX:maxX, minY:maxY]
        resized_cropped = cv2.resize(cropped, (int(width), int(height)))
        width_re = resized_cropped.shape[1]
        height_re = resized_cropped.shape[0]
        
        line_x = np.array([0]*22)
        line_y = np.array([0]*16)
        for i in range(22):
            line_x[i] = 5+30*i
        for i in range(16):
            line_y[i] = 2+30*i


        color_searching = (100,255,0)  # green
        color_swabing = (0,128,255)    # orange 
        color_warning = (0,0,255)      # red
        color_grid = (128,0,0)     # yellow


        if swab_state == 0:
            up_color = color_searching
            down_color = color_searching
            left_color = color_searching
            right_color = color_searching
            info_color = color_searching
            swabing_info = "Click left button to swab,"
            swabing_info2 = "double click right button to restart from stage1."
        else:
            up_color = color_swabing
            down_color = color_swabing
            left_color = color_swabing
            right_color = color_swabing
            info_color = color_swabing
            swabing_info = "Swabing......"

        target_x = (width_re//2 + tip_woffset)
        target_y = (height_re//2 + tip_hoffset)
        self.pub_lt.publish(swab_button_ui)

        #cv2.circle(resized_cropped, (target_x,target_y), 60, info_color, thickness=2)
        '''
        cv2.rectangle(resized_cropped,(160,0),(500,30),(255,255,255),-1)
        cv2.rectangle(resized_cropped,(160,0),(500,30),info_color,4)
        cv2.putText(resized_cropped, swabing_info, (240,18), cv2.FONT_HERSHEY_PLAIN,1, info_color, 1, cv2.LINE_AA)
        '''
        

        
        
        path = '/home/user0001/swab1.0.0_ws/src/swab-ros-main/camcam/test_pic'
        
        img = cv2.imread('/home/user0001/swab1.0.0_ws/src/swab-ros-main/camcam/src_pic/oral1.2.jpg')
        img_cropped = img[minX:maxX, minY:maxY]
        if state == 1:
            resized_cropped = cv2.resize(img_cropped, (int(width), int(height)))
            cv2.line(resized_cropped, (target_x-15,0), (target_x-15,height_re), color_grid, thickness=1)
            cv2.line(resized_cropped, (target_x+15,0), (target_x+15,height_re), color_grid, thickness=1)
            cv2.line(resized_cropped, (0,target_y-15), (width_re,target_y-15), color_grid, thickness=1)
            cv2.line(resized_cropped, (0,target_y+15), (width_re,target_y+15), color_grid, thickness=1)
            for i in range(16):
                cv2.line(resized_cropped, (target_x-15-30*(i+1),0), (target_x-15-30*(i+1),height_re), color_grid, thickness=1)
                cv2.line(resized_cropped, (target_x+15+30*(i+1),0), (target_x+15+30*(i+1),height_re), color_grid, thickness=1
                )
                cv2.line(resized_cropped, (0,target_y-15-30*(i+1)), (width_re,target_y-15-30*(i+1)), color_grid, thickness=1)
                cv2.line(resized_cropped, (0,target_y+15+30*(i+1)), (width_re,target_y+15+30*(i+1)), color_grid, thickness=1)
            #if record_1 == 0:
                #cv2.rectangle(resized_cropped,(80,0),(600,40),(255,255,255),-1)
                #cv2.rectangle(resized_cropped,(80,0),(600,40),info_color,4)
                #cv2.putText(resized_cropped, "please click left button to select grid.", (200,25), cv2.FONT_HERSHEY_PLAIN,1, info_color, 1, cv2.LINE_AA)
            if record_1 == 1:
                cv2.circle(resized_cropped, (550,400), 35, (0,0,255) , thickness=10)
                cv2.circle(resized_cropped, (550,400), 35, (255,255,255) ,-1)
                cv2.putText(resized_cropped, "confirm.", (520,405), cv2.FONT_HERSHEY_PLAIN,1, (0,0,255), 1, cv2.LINE_AA)            
                
                draw_x1 = 0
                draw_y1 = 0
                draw_x2= 0
                draw_y2 = 0
                #cv2.circle(resized_cropped,(mouseX,mouseY),100,(0,0,255),2)
                for i in range(22):
                    if(abs(mouseXD-line_x[i])<15):
                        if((mouseXD-line_x[i])>=0&(i+1)<22):
                            draw_x1 = line_x[i]
                            draw_x2 = line_x[i+1]
                        if((mouseXD-line_x[i])<0&(i-1)>=0):
                            draw_x1 = line_x[i-1]
                            draw_x2 = line_x[i]
                        break
                for i in range(16):
                    if(abs(mouseYD-line_y[i])<15):
                        if((mouseYD-line_y[i])>=0&(i+1)<16):
                            draw_y1 = line_y[i]
                            draw_y2 = line_y[i+1]
                        if((mouseYD-line_y[i])<0&(i-1)>=0):
                            draw_y1 = line_y[i-1]
                            draw_y2 = line_y[i]
                        break
                #print(draw_x1)
                #print(draw_y1)
                cv2.rectangle(resized_cropped,(draw_x1,draw_y1),(draw_x2,draw_y2),(0,0,255),2)            
            if shot_1 == 1:
                cv2.rectangle(resized_cropped,(draw_x1,draw_y1),(draw_x2,draw_y2),(0,255,255),2)                  
                cv2.imwrite(os.path.join(path , "1.1_test_{}_pic.jpeg".format(time.ctime())), resized_cropped)
                record_1 = 2
                shot_1 = 0
            if record_1 ==2:
                cv2.circle(resized_cropped, (550,400), 35, (100,255,0) , thickness=10)
                cv2.circle(resized_cropped, (550,400), 35, (255,255,255) ,-1)
                cv2.putText(resized_cropped, "next", (532,405), cv2.FONT_HERSHEY_PLAIN,1, (100,255,0), 1, cv2.LINE_AA)            
                
        if state == 2:
            cv2.line(resized_cropped, (target_x-15,0), (target_x-15,height_re), color_grid, thickness=1)
            cv2.line(resized_cropped, (target_x+15,0), (target_x+15,height_re), color_grid, thickness=1)
            cv2.line(resized_cropped, (0,target_y-15), (width_re,target_y-15), color_grid, thickness=1)
            cv2.line(resized_cropped, (0,target_y+15), (width_re,target_y+15), color_grid, thickness=1)
            for i in range(16):
                cv2.line(resized_cropped, (target_x-15-30*(i+1),0), (target_x-15-30*(i+1),height_re), color_grid, thickness=1)
                cv2.line(resized_cropped, (target_x+15+30*(i+1),0), (target_x+15+30*(i+1),height_re), color_grid, thickness=1
                )
                cv2.line(resized_cropped, (0,target_y-15-30*(i+1)), (width_re,target_y-15-30*(i+1)), color_grid, thickness=1)
                cv2.line(resized_cropped, (0,target_y+15+30*(i+1)), (width_re,target_y+15+30*(i+1)), color_grid, thickness=1)
            #if record_2 == 0:
                #cv2.rectangle(resized_cropped,(80,0),(600,40),(255,255,255),-1)
                #cv2.rectangle(resized_cropped,(80,0),(600,40),info_color,4)
                #cv2.putText(resized_cropped, "please click left button to select grid.", (200,25), cv2.FONT_HERSHEY_PLAIN,1, info_color, 1, cv2.LINE_AA)            
            if record_2 == 1:
                cv2.circle(resized_cropped, (550,400), 35, (0,0,255) , thickness=10)
                cv2.circle(resized_cropped, (550,400), 35, (255,255,255) ,-1)
                cv2.putText(resized_cropped, "confirm.", (520,405), cv2.FONT_HERSHEY_PLAIN,1, (0,0,255), 1, cv2.LINE_AA)            
                draw_x1 = 0
                draw_y1 = 0
                draw_x2= 0
                draw_y2 = 0
                #cv2.circle(resized_cropped,(mouseX,mouseY),100,(0,0,255),2)
                for i in range(22):
                    if(abs(mouseXD-line_x[i])<15):
                        if((mouseXD-line_x[i])>=0&(i+1)<22):
                            draw_x1 = line_x[i]
                            draw_x2 = line_x[i+1]
                        if((mouseXD-line_x[i])<0&(i-1)>=0):
                            draw_x1 = line_x[i-1]
                            draw_x2 = line_x[i]
                        break
                for i in range(16):
                    if(abs(mouseYD-line_y[i])<15):
                        if((mouseYD-line_y[i])>=0&(i+1)<16):
                            draw_y1 = line_y[i]
                            draw_y2 = line_y[i+1]
                        if((mouseYD-line_y[i])<0&(i-1)>=0):
                            draw_y1 = line_y[i-1]
                            draw_y2 = line_y[i]
                        break
                #print(draw_x1)
                #print(draw_y1)
                cv2.rectangle(resized_cropped,(draw_x1,draw_y1),(draw_x2,draw_y2),(0,0,255),2)            
            if shot_2 == 1:
                cv2.rectangle(resized_cropped,(draw_x1,draw_y1),(draw_x2,draw_y2),(0,255,255),2)                  
                cv2.imwrite(os.path.join(path , "2.1_test_{}_pic.jpeg".format(time.ctime())), resized_cropped)
                record_2 = 2
                shot_2 = 0
            if record_2 ==2:
                cv2.circle(resized_cropped, (550,400), 35, (100,255,0) , thickness=10)
                cv2.circle(resized_cropped, (550,400), 35, (255,255,255) ,-1)
                cv2.putText(resized_cropped, "next", (532,405), cv2.FONT_HERSHEY_PLAIN,1, (100,255,0), 1, cv2.LINE_AA)            
        if state == 3:
            #cv2.rectangle(resized_cropped,(100,0),(550,40),(255,255,255),-1)
            #cv2.rectangle(resized_cropped,(100,0),(550,40),info_color,4)
            if swab_state!=0:                
                cv2.putText(resized_cropped, swabing_info, (280,25), cv2.FONT_HERSHEY_PLAIN,1, info_color, 1, cv2.LINE_AA)
            if swab_state==0:       
                cv2.circle(resized_cropped, (550,400), 35, (100,255,0) , thickness=10)
                cv2.circle(resized_cropped, (550,400), 35, (255,255,255) ,-1)
                cv2.putText(resized_cropped, "swab?", (532,405), cv2.FONT_HERSHEY_PLAIN,1, (100,255,0), 1, cv2.LINE_AA) 
            if swab_button_ui == 1:
                cv2.circle(resized_cropped, (550,400), 35, (0,0,255) , thickness=10)
                cv2.circle(resized_cropped, (550,400), 35, (255,255,255) ,-1)
                cv2.putText(resized_cropped, "confirm", (520,405), cv2.FONT_HERSHEY_PLAIN,1, (0,0,255), 1, cv2.LINE_AA) 
                
        
        if state==3 and swab_button_ui !=1:
            cv2.line(resized_cropped, (target_x-10,target_y), (target_x+10,target_y), info_color, thickness=2)
            cv2.line(resized_cropped, (target_x,target_y-10), (target_x,target_y+10), info_color, thickness=2)
        if state == 3 and swab_state!= 0 and swab_button_ui!= 3:
            state_3_ban = 1
        if state == 3 and swab_state == 0 :
            state_3_ban = 0
        if state == 3 and swab_b == 3 and swab_state==0:
            cv2.circle(resized_cropped, (550,400), 35, (100,255,0) , thickness=10)
            cv2.circle(resized_cropped, (550,400), 35, (255,255,255) ,-1)
            cv2.putText(resized_cropped, "next", (532,405), cv2.FONT_HERSHEY_PLAIN,1, (100,255,0), 1, cv2.LINE_AA)            

        if swab_state == 2 :
            cv2.line(resized_cropped, (target_x-15,0), (target_x-15,height_re), color_grid, thickness=1)
            cv2.line(resized_cropped, (target_x+15,0), (target_x+15,height_re), color_grid, thickness=1)
            cv2.line(resized_cropped, (0,target_y-15), (width_re,target_y-15), color_grid, thickness=1)
            cv2.line(resized_cropped, (0,target_y+15), (width_re,target_y+15), color_grid, thickness=1)
            for i in range(16):
                cv2.line(resized_cropped, (target_x-15-30*(i+1),0), (target_x-15-30*(i+1),height_re), color_grid, thickness=1)
                cv2.line(resized_cropped, (target_x+15+30*(i+1),0), (target_x+15+30*(i+1),height_re), color_grid, thickness=1)
                cv2.line(resized_cropped, (0,target_y-15-30*(i+1)), (width_re,target_y-15-30*(i+1)), color_grid, thickness=1)
                cv2.line(resized_cropped, (0,target_y+15+30*(i+1)), (width_re,target_y+15+30*(i+1)), color_grid, thickness=1)
            cv2.rectangle(resized_cropped,(160,0),(500,30),(255,255,255),-1)
            cv2.rectangle(resized_cropped,(160,0),(500,30),info_color,4)
            cv2.putText(resized_cropped, swabing_info, (240,18), cv2.FONT_HERSHEY_PLAIN,1, info_color, 1, cv2.LINE_AA)
            cv2.imwrite(os.path.join(path , "2.2_test_{}_pic.jpeg".format(time.ctime())), resized_cropped)
            #time.sleep(1)
            swab_state = 1
            swab_b=3


        #print(pic_count)
        cv2.startWindowThread()
        cv2.namedWindow("camera", cv2.WND_PROP_FULLSCREEN)
        cv2.setMouseCallback("camera",dc)
        #cv2.setWindowProperty("camera",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
        cv2.imshow("camera", resized_cropped)

        function_list_name = init_canvas(750, 290, color=(128, 255, 255))
        cv2.putText(function_list_name, "Function Table : ", (20,50), cv2.FONT_HERSHEY_PLAIN,1, (0,0,255), 1, cv2.LINE_AA)
        cv2.putText(function_list_name, "zoom in / zoom out : mouse wheel up / down ", (35,80), cv2.FONT_HERSHEY_PLAIN,1, (0,0,255), 1, cv2.LINE_AA)
        cv2.putText(function_list_name, "to change state : double clik right button.", (35,110), cv2.FONT_HERSHEY_PLAIN,1, (0,0,255), 1, cv2.LINE_AA)
        #cv2.putText(function_list_name, "hide grid : double clik right button.", (35,140), cv2.FONT_HERSHEY_PLAIN,1, (0,0,255), 1, cv2.LINE_AA)
        cv2.putText(function_list_name, "select spectfic grid postion and screenshot : clik left button to select grid.", (35,140), cv2.FONT_HERSHEY_PLAIN,1, (0,0,255), 1, cv2.LINE_AA)
        cv2.putText(function_list_name, "                                          -to screenshot, double clik left button.", (35,170), cv2.FONT_HERSHEY_PLAIN,1, (0,0,255), 1, cv2.LINE_AA)
        cv2.putText(function_list_name, "                                          -to cancle, double clik middle button.", (35,200), cv2.FONT_HERSHEY_PLAIN,1, (0,0,255), 1, cv2.LINE_AA)
        cv2.putText(function_list_name, "swab : clik left button - to swab, double clik left button.", (35,230), cv2.FONT_HERSHEY_PLAIN,1, (0,0,255), 1, cv2.LINE_AA)
        cv2.putText(function_list_name, "                        - to cancle, double clik middle button.", (35,260), cv2.FONT_HERSHEY_PLAIN,1, (0,0,255), 1, cv2.LINE_AA)

        

        #cv2.startWindowThread()
        #cv2.namedWindow("function list", cv2.WND_PROP_FULLSCREEN)
        #cv2.imshow("function list", function_list_name)

        #print(target_x)
        #print(target_y)
        #print(" tet ")
  


def swab_state_callback(msg):
    global swab_state
    swab_state = msg.data

def dc(event,x,y,flags,param):
    global scale,grid
    global swab_button_ui
    global grid_record
    global mouseX,mouseY,mouseXD,mouseYD
    global pic_count
    global ui_ban
    global screen_shot_gogogo
    global screen_shot_ban
    global swab_state
    global state
    global record_1
    global shot_1
    global record_2
    global shot_2
    global state_1_ban
    global state_2_ban
    global state_3_ban
    global chang_state
    global swab_b
    global a

    if event == cv2.EVENT_LBUTTONDOWN :
        mouseX = x
        mouseY = y
        a=(pow((mouseX-550),2)+pow((mouseY-400),2))
    
    if state==1 and state_1_ban==0:
        state_2_ban = 1
        state_3_ban = 1
        if event == cv2.EVENT_LBUTTONDOWN and a>1225:
            record_1 = 1
            mouseXD = x
            mouseYD = y
        if event == cv2.EVENT_LBUTTONDBLCLK and record_1 == 1 and a<=1225:
            shot_1 = 1
        if event == cv2.EVENT_MBUTTONDBLCLK:
            record_1 = 0
        if event == cv2.EVENT_LBUTTONDBLCLK and record_1 == 2 and a<=1225:
            state = 2
            record_1 = 0
            shot_1 = 0
            state_2_ban = 0
            event = 0
    if state==2 and state_2_ban==0:
        record_1 = 0
        shot_1 = 0
        state_1_ban = 1
        state_3_ban = 1        
        if event == cv2.EVENT_LBUTTONDOWN and a>1225:
            record_2 = 1
            mouseXD = x
            mouseYD = y
        if event == cv2.EVENT_LBUTTONDBLCLK and record_2 == 1 and a<=1225:
            shot_2 = 1
        if event == cv2.EVENT_MBUTTONDBLCLK:
            record_2 = 0
        if event == cv2.EVENT_LBUTTONDBLCLK and record_2 == 2 and a<=1225:
            state = 3
            record_2 = 0
            shot_2 = 0
            state_3_ban = 0
            event = 0
    
    if state ==3 and state_3_ban==0:
        state_1_ban = 1
        state_2_ban = 1
        if event == cv2.EVENT_LBUTTONDBLCLK and swab_b != 3 and swab_button_ui != 1 and (pow((mouseX-550),2)+pow((mouseY-400),2))<=1225:
            swab_button_ui = 1
            event = 0
        if event == cv2.EVENT_LBUTTONDBLCLK and swab_b != 3 and swab_button_ui == 1 and (pow((mouseX-550),2)+pow((mouseY-400),2))<=1225:
                swab_button_ui = 2
                time.sleep(1)
                swab_button_ui = 0
        if event == cv2.EVENT_MBUTTONDBLCLK and swab_button_ui == 1:
            swab_button_ui = 0
        if event == cv2.EVENT_RBUTTONDBLCLK :
                swab_button_ui = 2
                time.sleep(1)
                swab_button_ui = 0
        if event == cv2.EVENT_LBUTTONDBLCLK and swab_b == 3 and swab_button_ui == 0 and (pow((mouseX-550),2)+pow((mouseY-400),2))<=1225:
            swab_button_ui = 0
            state = 1
            state_1_ban = 0
            event = 0
            swab_b=0
   
    if scale>100:
        scale = 100
    if scale <1:
        scale = 1
    else:
        if event == cv2.EVENT_MOUSEHWHEEL:
            if flags < 0:
                scale+=0.1
                #print("in!\n")
            if flags > 0:
                scale-=0.1
                #print("out!\n")
            
  
def main(args):
  ic = image_converter()
  rospy.init_node('image_converter', anonymous=True, disable_signals=True)
  try:
    rospy.spin()
  except KeyboardInterrupt:
    print("Shutting down")
  cv2.destroyAllWindows()

if __name__ == '__main__':
    main(sys.argv)
