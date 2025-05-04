import socket
import sys
from struct import unpack
from vpython import *
from time import *
import numpy as np
import math

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
host, port = '0.0.0.0', 64000
server_address = (host, port)

sock.bind(server_address)
print(f'Starting UDP server on {host} port {port}')

scene.range=5
toRad=2*np.pi/360
toDeg=1/toRad
scene.forward=vector(1,-1,0)
 
scene.width=600
scene.height=600
 
xarrow=arrow(lenght=2, shaftwidth=.1, color=color.red,axis=vector(1,0,0))
yarrow=arrow(lenght=2, shaftwidth=.1, color=color.green,axis=vector(0,1,0))
zarrow=arrow(lenght=4, shaftwidth=.1, color=color.blue,axis=vector(0,0,1))
 
frontArrow=arrow(length=4,shaftwidth=.1,color=color.purple,axis=vector(1,0,0))
upArrow=arrow(length=1,shaftwidth=.1,color=color.magenta,axis=vector(0,1,0))
sideArrow=arrow(length=2,shaftwidth=.1,color=color.orange,axis=vector(0,0,1))
 
bBoard=box(length=6,width=2,height=.2,opacity=.8,pos=vector(0,0,0,))
nano=box(lenght=1.75,width=.6,height=.1,pos=vector(2,.1+.05,0),color=color.green)
myObj=compound([bBoard,nano])

while True:
    # Wait for message
    message, address = sock.recvfrom(4027)
    p, r, y = unpack('3f', message)
    pitch, roll, yaw = p * toRad, r * toRad, y * toRad
    print(f'pitch: {pitch}, roll: {roll}, Z: {yaw}')

    rate(220)
    k=vector(cos(-yaw)*cos(pitch), sin(pitch), sin(-yaw)*cos(pitch))
    y=vector(0,1,0)
    s=cross(k,y)
    v=cross(s,k)
    vrot=v*cos(roll)+cross(k,v)*sin(roll)

    frontArrow.axis=k
    sideArrow.axis=cross(k,vrot)
    upArrow.axis=vrot
    myObj.axis=k
    myObj.up=vrot
    sideArrow.length=2
    frontArrow.length=4
    upArrow.length=1
