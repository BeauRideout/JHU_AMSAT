import time
import board
import busio
import os
import cv2
import numpy as np
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Define function to capture and save an image
def captureImage(filename="image.jpg", width = 768, height = 1024, timeout = 5000, shutter = 10000000):
    """
    The following function sets the  input paramaters and commands the Freenove FNK0056 camera to capture an image.

    Inputs:
        filename (str): output file name
        width (int): image width in pixels
        height (int): image height in pixels
        timeout (int): capture timeout in milliseconds
        shutter (int): camera exposure time in milliseconds
        
    Returns:
        str: absolute file path of the captured image
    """
    cmd = f"libcamera-jpeg -o {filename} -t {timeout} --width {width} --height {height} --shutter {shutter}"
    os.system(cmd)
    print(f"Captured image saved as {filename}")
    return os.path.abspath(filename)
        
# Process image for celestial body detection
def detectCircles(image_path, dp, minDist, param1, param2, minRadius, maxRadius):
    """
    The following function detects circles in an image using the Hough Circle Transform.

    Inputs:
        image_path (str): path of the image file to be processed
        dp (float): inverse ratio of the accumulator resolution to the image resolution
        minDist (int): minimum distance between circle centers
        param1 (int): higher threshold for the Canny edge detector
        param2 (int): accumulator threshold for the circle centers at the detection stage
        minRadius (int): minimum circle radius in pixels
        maxRadius (int): maximum circle radius in pixels (enter 0 for no limit)
        
    Returns:
        image (ndarray): the original image with detected circles highlighted
        circles (ndarray or None): array of detected circles (returned as [x, y, radius]) or None
        
    References:
        OpenCV-Python: https://docs.opencv.org/4.x/d2/d96/tutorial_py_table_of_contents_imgproc.html
        Hough Transform: https://www.sciencedirect.com/science/article/abs/pii/S0957417415008210
    """
    # Load a captured image
    image = cv2.imread(image_path)
    if image is None:
        print("Error: Image not found:", image_path)
        return None, []
        
    # Convert image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)

    # Use the Hough Transform to detect circular objects
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp = dp, minDist = minDist, param1 = param1, param2 = param2, minRadius = minRadius, maxRadius = maxRadius)

    # Highlight detected circles
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            center = (i[0], i[1])
            radius = i[2]
            # Draw detected circle centers
            cv2.circle(image, center, 2, (0, 255, 0), 3)
            # Draw detected cirlce edges
            cv2.circle(image, center, radius, (0, 255, 0), 3)
            
    return image, circles

# Define a function to montor light conditions and capture an image when optimal
def monitorLight(light_threshold, check_interval):
    """
    The following function monitors the ambient light level to capture images only when specified light conditions are met.

    Inputs:
        light_threshold (int): ADC reading threshold to trigger image capture
        check_interval (int): time between light sensor checks in seconds
        
    Returns:
        str: the absolute file path of the captured image
    """
    # Initialize I2C bus and ADS1115 ADC
    i2c = busio.I2C(board.SCL, board.SDA)
    ads = ADS.ADS1115(i2c)
    channel = AnalogIn(ads, ADS.P3)
    
    print("Monitoring ambient light...")

    while True:
        print("Current light level:", channel.value)
        if channel.value > light_threshold:
            filename = f"image_{int(time.time())}.jpg"
            image_path = captureImage(filename=filename)
            # Exit loop once an image is captured
            return image_path
        time.sleep(check_interval)
        
def main():
    # Monitor light and campture an image when optimal consitions are reached
    image_file = monitorLight(1000, 5)
    print("Image captured at:", image_file)
    
    # Process the captured image for circles
    processed_image, circles = detectCircles(image_file, 1.2, 20, 40, 91, 10, 200)
    
    if processed_image is not None:
        print("Objects detected:", circles)
        cv2.imshow("Detected Objects", processed_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("No objects detected.")

# ------------EXECUTION------------
if __name__ == "__main__":
    main()
