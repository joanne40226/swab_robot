#! /usr/bin/env python3
import socket
import time
import rospy
import roslaunch
from std_msgs.msg import Int16, String
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Path
import numpy as np


def joy_callback_lai(msg):
    limit_data = "0000"
    joy_data = msg.data
    #print(joy_data)

    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect(("192.168.0.4", 80))

    # request_line = "GET /paramC01=%.3f*%.3f HTTP/1.1\r\n" % (1.234, 0.257)
    request_line = "GET /paramC01=" + joy_data
    request_line = request_line + " HTTP/1.1\r\n"
    request_header = "Host: 192.168.0.4\r\n"
    User_Agent = "\r\n"
    request_data = request_line + request_header + User_Agent + "\r\n"

    tcp_socket.send(request_data.encode())
    recv_data = tcp_socket.recv(50)
    recv_data = recv_data.decode()
    #print(recv_data) //print data from f28

    # limit_data = tcp_socket.recv(1024)
    # limit_pub.publish(str(ord(
    #     limit_data[0]))+str(ord(limit_data[1]))+str(ord(limit_data[2]))+str(ord(limit_data[3])))

    tcp_socket.close()


if __name__ == '__main__':
    rospy.init_node('http_f28388')
    joy_topic = "/joy_information"
    position_topic = "/position"
    limit_pub = rospy.Publisher("limit_switch_state", String, queue_size=10)
    rospy.Subscriber(joy_topic, String, joy_callback_lai,
                     queue_size=1, buff_size=52428800)

    rospy.spin()
