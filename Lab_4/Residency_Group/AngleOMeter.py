
#Connections
#MPU6050 - Raspberry pi
#VCC - 5V  (2 or 4 Board)
#GND - GND (6 - Board)
#SCL - SCL (5 - Board)
#SDA - SDA (3 - Board)


from Kalman import KalmanAngle
import smbus			#import SMBus module of I2C
import time
import math
from gpiozero import LED
import RPi.GPIO
import paho.mqtt.client as mqtt

mqttBroker = "mqtt.eclipseprojects.io"
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "Gyro_output")
client.connect(mqttBroker)


LEDX = LED(1)
LEDY = LED(7)
LEDZ = LED(8)

LEDX.on()
LEDY.on()
LEDZ.on()

kalmanX = KalmanAngle()
kalmanY = KalmanAngle()


RestrictPitch = True	#Comment out to restrict roll to ±90deg instead - please read: http://www.freescale.com/files/sensors/doc/app_note/AN3461.pdf
radToDeg = 57.2957786
kalAngleX = 0
kalAngleY = 0


#some MPU6050 Registers and their Address
PWR_MGMT_1   = 0x6B
SMPLRT_DIV   = 0x19
CONFIG       = 0x1A
GYRO_CONFIG  = 0x1B
INT_ENABLE   = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H  = 0x43
GYRO_YOUT_H  = 0x45
GYRO_ZOUT_H  = 0x47


#Read the gyro and acceleromater values from MPU6050
def MPU_Init():
	#write to sample rate register
	bus.write_byte_data(DeviceAddress, SMPLRT_DIV, 7)

	#Write to power management register
	bus.write_byte_data(DeviceAddress, PWR_MGMT_1, 1)

	#Write to Configuration register
	#Setting DLPF (last three bit of 0X1A to 6 i.e '110' It removes the noise due to vibration.) https://ulrichbuschbaum.wordpress.com/2015/01/18/using-the-mpu6050s-dlpf/
	bus.write_byte_data(DeviceAddress, CONFIG, int('0000110',2))

	#Write to Gyro configuration register
	bus.write_byte_data(DeviceAddress, GYRO_CONFIG, 0)

	#Write to interrupt enable register
	bus.write_byte_data(DeviceAddress, INT_ENABLE, 1)


def read_raw_data(addr):
	#Accelero and Gyro value are 16-bit
	high = bus.read_byte_data(DeviceAddress, addr)
	low = bus.read_byte_data(DeviceAddress, addr+1)

	#concatenate higher and lower value
	value = ((high << 8) | low)

	#to get signed value from mpu6050
	if(value > 32768):
		value = value - 65536
	return value


bus = smbus.SMBus(1) 	# or bus = smbus.SMBus(0) for older version boards
DeviceAddress = 0x68   # MPU6050 device address

MPU_Init()

time.sleep(1)
#Read Accelerometer raw value
accX = read_raw_data(ACCEL_XOUT_H)
accY = read_raw_data(ACCEL_YOUT_H)
accZ = read_raw_data(ACCEL_ZOUT_H)

if (RestrictPitch):
	roll = math.atan2(accY,accZ)*radToDeg
	pitch = math.atan(-accX/math.sqrt((accY**2)+(accZ**2)))*radToDeg
	
else:
	roll = math.atan(accY/math.sqrt((accX**2)+(accZ**2)))*radToDeg
	pitch = math.atan2(-accX,accZ)*radToDeg
	

kalmanX.setAngle(roll)
kalmanY.setAngle(pitch)

gyroXAngle = roll;
gyroYAngle = pitch;

compAngleX = roll;
compAngleY = pitch;


timer = time.time()
flag = 0


yaw = 0

while True:
	if(flag >100): #Problem with the connection
		print("There is a problem with the connection")
		flag=0
		continue
	try:
		#Read Accelerometer raw value
		accX = read_raw_data(ACCEL_XOUT_H)
		accY = read_raw_data(ACCEL_YOUT_H)
		accZ = read_raw_data(ACCEL_ZOUT_H)

		#Read Gyroscope raw value
		gyroX = read_raw_data(GYRO_XOUT_H)
		gyroY = read_raw_data(GYRO_YOUT_H)
		gyroZ = read_raw_data(GYRO_ZOUT_H)

		dt = time.time() - timer
		timer = time.time()
	
		gyroXRate = gyroX/131
		gyroYRate = gyroY/131
		gyroZRate = gyroZ/131

		#Insert equations for Yaw and add parts for the Z angles
		if (RestrictPitch):
			roll = math.atan2(accY,accZ) * radToDeg
			pitch = math.atan(-accX/math.sqrt((accY**2)+(accZ**2))) * radToDeg
			yaw += gyroZRate * dt
		else:
			roll = math.atan(accY/math.sqrt((accX**2)+(accZ**2))) * radToDeg
			pitch = math.atan2(-accX,accZ) * radToDeg
			yaw += gyroZRate * dt
		
		
	
		if (RestrictPitch):

			if((roll < -90 and kalAngleX >90) or (roll > 90 and kalAngleX < -90)):
				kalmanX.setAngle(roll)
				complAngleX = roll
				kalAngleX   = roll
				gyroXAngle  = roll
			else:
				kalAngleX = kalmanX.getAngle(roll,gyroXRate,dt)
			

			if(abs(kalAngleX)>90):
				gyroYRate  = -gyroYRate
				kalAngleY  = kalmanY.getAngle(pitch,gyroYRate,dt)
		else:

			if((pitch < -90 and kalAngleY >90) or (pitch > 90 and kalAngleY < -90)):
				kalmanY.setAngle(pitch)
				complAngleY = pitch
				kalAngleY   = pitch
				gyroYAngle  = pitch
			else:
				kalAngleY = kalmanY.getAngle(pitch,gyroYRate,dt)

			if(abs(kalAngleY)>90):
				gyroXRate  = -gyroXRate
				kalAngleX = kalmanX.getAngle(roll,gyroXRate,dt)

		#angle = (rate of change of angle) * change in time; add for Z axis
		gyroXAngle = gyroXRate * dt
		gyroYAngle = gyroYRate * dt

		#compAngle = constant * (old_compAngle + angle_obtained_from_gyro) + constant * angle_obtained from accelerometer; add for Z axis
		compAngleX = 0.93 * (compAngleX + gyroXRate * dt) + 0.07 * roll
		compAngleY = 0.93 * (compAngleY + gyroYRate * dt) + 0.07 * pitch

		if ((gyroXAngle < -180) or (gyroXAngle > 180)):
			gyroXAngle = kalAngleX
		if ((gyroYAngle < -180) or (gyroYAngle > 180)):
			gyroYAngle = kalAngleY


		print("Angle X: " + str(roll)+"   " +"Angle Y: " + str(pitch)+"Angle Z: "+str(yaw))
		#print(str(roll)+"  "+str(gyroXAngle)+"  "+str(compAngleX)+"  "+str(kalAngleX)+"  "+str(pitch)+"  "+str(gyroYAngle)+"  "+str(compAngleY)+"  "+str(kalAngleY)+"  "+str(yaw)+"  "+str(gyroZAngle)+"  "+str(compAngleZ)+"  "+str(kalAngleZ))
		
		
		if ((abs(roll) > 65) and (abs(roll) < 75)):
			LEDX.on()
		else:
			LEDX.off()
		
		if ((abs(pitch) > 55) and (abs(pitch) < 65)):
			LEDY.on()
		else:
			LEDY.off()
		
		
		if ((abs(yaw) > 10) and (abs(yaw) < 20)):
			LEDZ.on()
		else:
			LEDZ.off()
		
		msg = str(roll) + "," +str(pitch)+","+str(yaw)
		client.publish("attitude", msg)
		print("Just published" + str(msg) + " to attitude")
		time.sleep(0.005)
			
	except Exception as exc:
		flag += 1
		print(exc)
