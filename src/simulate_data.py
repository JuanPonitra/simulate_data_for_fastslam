#!/usr/bin/env python3

import math
import numpy as np
import rospy
from fiducial_msgs.msg import FiducialTransformArray, FiducialTransform
from nav_msgs.msg import Odometry
from std_msgs.msg import Header
from geometry_msgs.msg import Quaternion, Pose, Point, Twist, Vector3

flag = False

def publish_data(filename, publish_frequency, landmarks, length):

    # Initialize global variables
    global flag

    # Create publisher for the extracted values
    pub = rospy.Publisher('pose', Odometry, queue_size=10)

    # Set the desired publishing frequency
    rate = rospy.Rate(publish_frequency)

    # Read the file line by line
    with open(filename, 'r') as file:

        for line in file:
            # Skip lines until reaching the line with values
            if line.startswith("# Fuck ton of points (x, y, theta)"):
                break

        for line in file:
            # Extract values from the line
            values = line.strip()[1:-1].split(',')

            # Convert values to float
            x = float(values[0])
            y = float(values[1])
            theta = (float(values[2]) * math.pi) / 180

            # Skip first iteration since we don't have previous values
            if flag == False:
                line_vel = [0, 0, 0]
                ang_vel = 0
                flag = True
            else:
                line_vel = abs((x-previous_pos[0])*publish_frequency + (y-previous_pos[1])*publish_frequency)
                ang_vel = (theta - previous_pos[2])*publish_frequency

            # Create ROS message
            odom = Odometry()
            current_time = rospy.Time.now()

            # Populate the header
            odom.header.stamp = current_time
            odom.header.frame_id = 'odom'

            # Set the pose information
            odom.pose.pose = Pose(Point(x, y, 0), Quaternion(0, 0, theta, 0))

            # Set the twist information
            odom.child_frame_id = 'base_link'
            odom.twist.twist = Twist(Vector3(line_vel, 0, 0), Vector3(0, 0, ang_vel))

            # Save this position
            previous_pos = [x, y, theta]

            # Publish the Odometry message
            pub.publish(odom)

            # Get fiducial transforms for landmarks the robot recognizes (WIP)
            get_fid_transforms(landmarks, length, x, y, theta)

            rate.sleep()

def transform_coordinates(x, y, theta, x_fid, y_fid):

    # Compute the relative position vector
    dx = x_fid - x
    dy = y_fid - y        

    # Apply rotation to align the vector with the robot's reference frame
    x_relative = dx * math.cos(theta) + dy * math.sin(theta)
    y_relative = -dx * math.sin(theta) + dy * math.cos(theta)

    # Calculate the absolute angle of the relative position vector
    theta_absolute = math.atan2(dy, dx)

    # Compute the relative angle
    theta_relative = theta_absolute - theta

    return x_relative, y_relative, theta_relative

def check_fov(x_fid, y_fid, length):
    # Current fov at 45º angle
    if abs(y_fid) <= x_fid and 0 < x_fid < length:
        return True
    else:
        return False

def get_fid_transforms(landmarks, length, x, y, theta):

    # Create publisher for the FiducialTransformArray
    pub = rospy.Publisher('fiducial_transforms', FiducialTransformArray, queue_size=10)

    # Create a FiducialTransformArray message
    transform_array_msg = FiducialTransformArray()    
    transform_array_msg.header = Header()
    transform_array_msg.header.stamp = rospy.Time.now()
    transform_array_msg.header.frame_id = 'robot_frame'  # Set the frame ID according to your setup   
    
    transformed_landmarks = []

    for landmark in landmarks:
        x_fid, y_fid = float(landmark[0]), float(landmark[1])

        x_local, y_local, theta_relative = transform_coordinates(x, y, theta, x_fid, y_fid)

        # If the landmark is not within robot fov, skips landmark
        if check_fov(x_local, y_local, length) == False:
            continue

        # Create a FiducialTransform message
        transform_msg = FiducialTransform() 
        # Set the fiducial ID
        transform_msg.fiducial_id = int(landmark[2])
        # Set the position and orientation in the local reference frame
        transform_msg.transform.translation.z = x_local
        transform_msg.transform.translation.x = -y_local
        transform_msg.transform.rotation.z = math.sin(theta_relative / 2)
        transform_msg.transform.rotation.w = math.cos(theta_relative / 2)

        # Append the transform message to the array
        transform_array_msg.transforms.append(transform_msg)

        transformed_landmarks.append([x_local, y_local, theta_relative])

    # Publish the FiducialTransformArray message
    pub.publish(transform_array_msg)

if __name__ == '__main__':

    # Initialize ROS node
    rospy.init_node('data_sim')

    # Specify the file path
    file_path_mov = '/home/juan/Desktop/Movement.txt'
    file_path_landmarks = '/home/juan/Desktop/Landmarks.txt'

    # Initialize local variables
    landmarks = []
    length = 3

    # Read the file line by line, saves landmark positions inside a variable
    with open(file_path_landmarks, 'r') as file:

        for line in file:
            # Skip lines until reaching the line with values
            if line.startswith("# 24 Point collection, 4 landmarks in each corner, 2 in the middle of each corridor"):
                break

        for line in file:
            # Extract values from the line
            values = line.strip()[1:-1].split(',')
            landmarks.append(values)

    # Specify the desired publishing frequency (in Hz)
    publish_frequency = 10  # 10 Hz

    try:
        publish_data(file_path_mov, publish_frequency, landmarks, length)
    except rospy.ROSInterruptException:
        pass
