from vpython import *
import paho.mqtt.client as mqtt
import time
import numpy as np

#  Offest from center for each object
offset_left = -5 
offset_right = 5

scene.forward=vector(1,-1,0)
toRad=2*np.pi/360

scene.width=800
scene.height=800

# Breadboard Model
xarrow=arrow(pos=vec(0,0,offset_left), length=2, shaftwidth=.1, color=color.red,axis=vector(1,0,0))
yarrow=arrow(pos=vec(0,0,offset_left), length=2, shaftwidth=.1, color=color.green,axis=vector(0,1,0))
zarrow=arrow(pos=vec(0,0,offset_left), length=4, shaftwidth=.1, color=color.blue,axis=vector(0,0,1))
 
frontArrow=arrow(pos=vec(0,0,offset_left), length=4,shaftwidth=.1,color=color.purple,axis=vector(1,0,0))
upArrow=arrow(pos=vec(0,0,offset_left), length=1,shaftwidth=.1,color=color.magenta,axis=vector(0,1,0))
sideArrow=arrow(pos=vec(0,0,offset_left), length=2,shaftwidth=.1,color=color.orange,axis=vector(0,0,1))
 
bBoard=box(pos=vec(0,0,offset_left), length=6,width=2,height=.2,opacity=.8)
nano=box(pos=vector(2,.1+.05, offset_left), length=1.75,width=.6,height=.1, color=color.green)
myObj=compound([bBoard,nano])

# CubeSat Model
body = box(pos=vec(0,0,offset_right), length =4, height=4, width=4, color=color.cyan)
panel1 = box(pos=vec(1.9,0,3 + offset_right), length=0.2, height=4, width=4, color=color.magenta)
panel2 = box(pos=vec(1.9,0,-3 + offset_right), length=0.2, height=4, width=4, color=color.magenta)

spacecraft = compound([body,panel1,panel2])

# MQTT Client Definition
class vpClient:
    def __init__(self):
        mqttBroker = 'mqtt.eclipseprojects.io'
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "GNCVis")
        self.client.connect(mqttBroker)
        self.client.loop_start()
        self.client.subscribe("attitude")
        self.msg = ""
        self.client.on_message = self.on_message

    # Message handler
    def on_message(self, client, userdata, message):
        self.msg = str(message.payload.decode("utf-8"))

# Initilize MQTT client
vpc = vpClient()

# Initialize roll, pitch, yaw to zero 
roll = 0
yaw = 0
pitch = 0
while True:
    # Split messages as they are received 
    vals = vpc.msg.split(",")
    if len(vals) == 3:
        pitch = float(vals[0]) * toRad
        roll = float(vals[1]) * toRad
        yaw = float(vals[2]) * toRad
    
    print(roll, pitch, yaw)
    rate(220)

    # Calculate vector pointing based on roll, pitch, and yaw values
    # Helpuful links: https://toptechboy.com/9-axis-imu-lesson-20-vpython-visualization-of-roll-pitch-and-yaw/
    k=vector(cos(-yaw)*cos(pitch), sin(pitch), sin(-yaw)*cos(pitch))
    y=vector(0,1,0)
    s=cross(k,y)
    v=cross(s,k)
    vrot=v*cos(roll)+cross(k,v)*sin(roll)

    # Move breadboard object to match IMU
    frontArrow.axis=k
    sideArrow.axis=cross(k,vrot)
    upArrow.axis=vrot
    myObj.axis=k
    myObj.up=vrot
    sideArrow.length=2
    frontArrow.length=4
    upArrow.length=1

    # Move CubeSat object to match IMU
    spacecraft.axis=k
    spacecraft.up=vrot
