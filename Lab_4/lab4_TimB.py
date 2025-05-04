import smbus
from Kalman import KalmanAngle
from gpiozero import LED
import time
import math

# Determine the angles needed to turn on the LEDs
ledXAng = 70 # [°]
ledYAng = 120 # [°]
ledZAng = 15 # [°]
ang_tol = 5 # [°] ± tolerance to the angle check

# Determine the pins for the LEDs
ledX = LED(7) # For the X axis (red)
ledY = LED(25) # For the Y axis (green)
ledZ = LED(8) # For the Z axis (blue)

# Either pitch or roll needs to be restricted to ±90°
RestrictPitch = False

# Initialize some global variables
kalmanX = KalmanAngle()
kalmanY = KalmanAngle()
kalmanZ = KalmanAngle()
kalAngleX = 0 # [°]
kalAngleY = 0 # [°]
kalAngleZ = 0 # [°]

# Initialize some calibration values
gyroXOffset = 0
gyroYOffset = 0
gyroZOffset = 0

# MPU6050 Registers and their Address
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

# GYRO_CONFIG
# X     Sensitivity     Scale Factor
# 0     ±250 °/s	    131
# 1	    ±500 °/s	    65.5
# 2	    ±1000 °/s	    32.8
# 3	    ±2000 °/s	    16.4

# Read the gyro and acceleromater values from MPU6050
def MPU_Init():
	# Write to sample rate register
	bus.write_byte_data(DeviceAddress, SMPLRT_DIV, 7)

	# Write to power management register
	bus.write_byte_data(DeviceAddress, PWR_MGMT_1, 1)

	# Write to Configuration register
	# Setting DLPF (last three bit of 0X1A to 6 i.e '110' It removes the noise due to vibration.) https://ulrichbuschbaum.wordpress.com/2015/01/18/using-the-mpu6050s-dlpf/
	bus.write_byte_data(DeviceAddress, CONFIG, int('0000110',2))

	# Write to Gyro configuration register
	bus.write_byte_data(DeviceAddress, GYRO_CONFIG, 0)

	# Write to interrupt enable register
	bus.write_byte_data(DeviceAddress, INT_ENABLE, 1)

# Read data directly from the sensor
def read_raw_data(addr):
	# Accelerometer and Gyro value are 16-bit
		high = bus.read_byte_data(DeviceAddress, addr)
		low = bus.read_byte_data(DeviceAddress, addr+1)

		# Concatenate higher and lower value
		value = ((high << 8) | low)

		# To get signed value from mpu6050
		if(value > 32768):
				value = value - 65536
		return value

# Assuming the sensor is not moving at initialization, this will determine the bias in the sensor to try to combat drift
def calibrate_gyro (samples):
	print("Calibrating gyroscope, keep the device still...")

	# Initialize offsets
	gyroXOffset = 0
	gyroYOfffset = 0
	gyroZOffset = 0

	for i in range(samples):
		gyroX = read_raw_data(GYRO_XOUT_H)
		gyroY = read_raw_data(GYRO_YOUT_H)
		gyroZ = read_raw_data(GYRO_ZOUT_H)

		gyroXOffset += gyroX
		gyroYOfffset += gyroY
		gyroZOffset += gyroZ

		time.sleep(0.005)
	
	# Calculate averages
	gyroXOffset /= samples
	gyroYOfffset /= samples
	gyroZOffset /= samples

	print("Calibration finish!\tX Offset: {:4.3f} Y Offset: {:4.3f} Z Offset: {:4.3f}".format(gyroXOffset, gyroYOffset, gyroZOffset))

	return gyroXOffset, gyroYOffset, gyroZOffset

# Turns an array of LEDs on with a ping pong animation to make sure everything is wired correctly
def test_leds (led_array, delay, loops):
	arr = list(range(len(led_array)))
	anim = arr + arr[:-1][::-1]
	full_anim = anim
	for i in range(loops): # number of times the ping pong animation will loop
		full_anim += anim[1:]

	# Play the animation
	for a in full_anim:
		for b in full_anim:
			if a == b:
				led_array[b].on()
			else:
				led_array[b].off()
		time.sleep(delay)
	
	# Make sure all the LEDs are off
	for k in range(len(led_array)):
		led_array[k].off()

# Initialize the sensor
print("Initializing sensor...")
bus = smbus.SMBus(1) # or bus = smbus.SMBus(0) for older version boards
DeviceAddress = 0x68 # MPU6050 device address
MPU_Init()
time.sleep(1)

print("Testing LEDs")
test_leds([ledX, ledY, ledZ], 0.1, 1)

# Calibrate gyroscope to minimize drift
gyroXOffset, gyroYOffset, gyroZOffset = calibrate_gyro(500)

print("Proceeding to main program!")
# Take initial readings

# Read raw acceleration values
accX = read_raw_data(ACCEL_XOUT_H)
accY = read_raw_data(ACCEL_YOUT_H)
accZ = read_raw_data(ACCEL_ZOUT_H)

# Initialize roll, pitch and yaw values
if RestrictPitch:
	roll = math.degrees(math.atan2(accY, accZ))
	pitch = math.degrees(math.atan2(-accX, math.sqrt((accY**2) + (accZ**2))))
	yaw = 0
else:
	roll = math.degrees(math.atan2(accY, math.sqrt((accX**2) + (accZ**2))))
	pitch = math.degrees(math.atan2(-accX, accZ))
	yaw = 0

# Initialize the gyro angles
gyroXAngle = roll
gyroYAngle = pitch
gyroZAngle = yaw

# Initialize Kalman and complementary filter values
kalmanX.setAngle(roll)
kalmanY.setAngle(pitch)
kalmanZ.setAngle(yaw)
compAngleX = roll
compAngleY = pitch
compAngleZ = yaw

# Set timer to find dt
timer = time.time()

# Set to throw errors in main loop
flag = 0

while True:
	if flag > 100: # Problem with connection
		print("There is a problem with the connection")
		flag = 0
		continue
	try:
		# Calculate delta time and reset timer
		dt = time.time() - timer # [s]
		timer = time.time()

		# Read Gyroscope raw values
		gyroX = read_raw_data(GYRO_XOUT_H)
		gyroY = read_raw_data(GYRO_YOUT_H)
		gyroZ = read_raw_data(GYRO_ZOUT_H)

		gyroX -= gyroXOffset
		gyroY -= gyroYOffset
		gyroZ -= gyroZOffset

		# Convert gyro data to deg/s
		gyroXRate = gyroX / 131 # [°/s]
		gyroYRate = gyroY / 131 # [°/s]
		gyroZRate = gyroZ / 131 # [°/s]

		# Read Accelerometer raw values
		accX = read_raw_data(ACCEL_XOUT_H)
		accY = read_raw_data(ACCEL_YOUT_H)
		accZ = read_raw_data(ACCEL_ZOUT_H)

		# Calculate roll, pitch and yaw using either XYZ or YXZ sequence
		if RestrictPitch:
			roll = math.degrees(math.atan2(accY, accZ))
			pitch = math.degrees(math.atan2(-accX, math.sqrt((accY**2) + (accZ**2))))
			yaw += gyroZRate * dt

			# If roll angle jumps past 90 to -90, reset Kalman filter
			if((roll < -90 and kalAngleX > 90) or (roll > 90 and kalAngleX < -90)):
				kalmanX.setAngle(roll)
				compAngleX = roll
				kalAngleX = roll
				gyroXAngle = roll
			else:
				kalAngleX = kalmanX.getAngle(roll, gyroXRate, dt)
			
			kalAngleY = kalmanY.getAngle(pitch, gyroYRate, dt)

			# Gimbal lock compensation
			if(abs(kalAngleX) > 90):
				gyroYRate = - gyroYRate
				kalAngleY = kalmanY.getAngle(pitch, gyroYRate, dt)
		else:
			roll = math.degrees(math.atan2(accY, math.sqrt((accX**2) + (accZ**2))))
			pitch = math.degrees(math.atan2(-accX, accZ))
			yaw += gyroZRate * dt

			# If pitch angle jumps past 90 to -90, reset Kalman filter
			if((pitch < -90 and kalAngleY > 90) or (pitch > 90 and kalAngleY < -90)):
				kalmanY.setAngle(pitch)
				compAngleY = pitch
				kalAngleY = pitch
				gyroYAngle = pitch
			else:
				kalAngleY = kalmanY.getAngle(pitch, gyroYRate, dt)

			kalAngleX = kalmanX.getAngle(roll, gyroXRate, dt)

			# Gimbal lock compensation
			if(abs(kalAngleY) > 90):
				gyroXRate = - gyroXRate
				kalAngleX = kalmanX.getAngle(roll, gyroXRate, dt)

		# If yaw angle jumps past -90 or 90, reset the Kalman filter
		if((yaw < -180 and kalAngleZ > 180) or (yaw > 180 and kalAngleZ < -180)):
			kalmanZ.setAngle(yaw)
			compAngleZ = yaw
			kalAngleZ = yaw
			gyroAngleZ = yaw
		else:
			kalAngleZ = kalmanZ.getAngle(yaw, gyroZRate, dt)

		# Calculate angle based on integration of gyro data
		# angle = (rate of change of angle) * change in time
		gyroXAngle = gyroXRate * dt
		gyroYAngle = gyroYRate * dt
		gyroZAngle += gyroZRate * dt

		# Apply Complementary filter between accel angle and gyro angle
		# compAngle = constant * (old_compAngle + angle_obtained_from_gyro) + constant * angle_obtained from accelerometer
		alpha = 0.93
		compAngleX = alpha * (compAngleX + gyroXRate * dt) + (1 - alpha) * roll
		compAngleY = alpha * (compAngleY + gyroYRate * dt) + (1 - alpha) * pitch
		compAngleZ = alpha * (compAngleZ + gyroZRate * dt) + (1 - alpha) * yaw

		print("Angle X: {:<5.1f}\tAngle Y: {:<5.1f}\tAngle Z: {:<5.1f}".format(kalAngleX, kalAngleY, kalAngleZ))

		# Check the angles against the LEDs specified angles and turn them on accordingly
		if abs(kalAngleX - ledXAng) < ang_tol:
			ledX.on()
		else:
			ledX.off()

		if abs(kalAngleY - ledYAng) < ang_tol:
			ledY.on()
		else:
			ledY.off()

		if abs(kalAngleZ - ledZAng) < ang_tol:
			ledZ.on()
		else:
			ledZ.off()


		time.sleep(0.005)
	except Exception as exc:
		flag += 1
	