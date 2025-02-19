import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.layers import DepthwiseConv2D
from tensorflow.keras.utils import register_keras_serializable
import cv2
import numpy as np
import time
import os
import math
from pyfirmata2 import Arduino, SERVO, util

def crop_image_by_size(image):
    crop_width = 230
    crop_height = 230
    """Crop the image to a fixed size from the center and save to the specified path."""
    # Load the image 
    # Get image dimensions
    img_height, img_width = image.shape[:2]
    
    # Ensure the crop dimensions are valid
    if crop_width > img_width or crop_height > img_height:
        print(f"Crop size is larger than the original image for {image}. Skipping.")
        return
    
    # Calculate the center of the image
    center_x, center_y = img_width / (1.6), img_height / (1.375)

    # Calculate the crop box
    x1 = math.floor(center_x - (crop_width / 2))
    y1 = math.floor(center_y - (crop_height / 2))
    x2 = math.floor(center_x + (crop_width / 2))
    y2 = math.floor(center_y + (crop_height / 2))

    # Perform the crop
    cropped_img = image[y1:y2, x1:x2]
    return cropped_img


# Disable scientific notation for clarity
np.set_printoptions(suppress=True)
print("TensorFlow version:", tf.__version__)

# Register custom DepthwiseConv2D for serialization/deserialization
@register_keras_serializable()
class CustomDepthwiseConv2D(DepthwiseConv2D):
    def __init__(self, **kwargs):
        if 'groups' in kwargs:
            kwargs.pop('groups')  # Remove unsupported argument
        super().__init__(**kwargs)

# Verify the model file exists
if not os.path.exists('Users\nareddulas3557\Documents\GitHub\DRS-Screw-Sorter-Code\converted_keras (4)\keras_model.h5'):
   print("Error: keras_model.h5 not found. Please ensure the file is in the same directory.")
   exit()

# Load the .h5 model with custom DepthwiseConv2D
try:
    model = load_model('keras_model.h5', custom_objects={'DepthwiseConv2D': CustomDepthwiseConv2D})
    print("Model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")
    exit()

# Verify the labels file exists
if not os.path.exists('labels.txt'):
    print("Error: labels.txt not found. Please ensure the file is in the same directory.")
    exit()

# Load class names
class_names = open('labels.txt', 'r').readlines()

# Initialize the camera
camera_index = 1  # Change to 1 or higher for a USB-connected camera
camera = cv2.VideoCapture(camera_index)
if not camera.isOpened():
    print(f"Error: Could not access camera with index {camera_index}.")
    exit()

# Main function for capturing and predicting
def catScrew():
    # Grab the camera's image
        ret, image = camera.read()
        if not ret:
            print("Error: Failed to capture image from camera.")

        # Resize the raw image to (224, 224) pixels
        cropped_image = crop_image_by_size(image)
        image_resized = cv2.resize(cropped_image, (224, 224), interpolation=cv2.INTER_AREA)

        # Show the image in a window
        cv2.imshow("Webcam Image", image_resized)

        # Preprocess the image for the model
        image_array = np.asarray(image_resized, dtype=np.float32).reshape(1, 224, 224, 3)
        image_array = (image_array / 127.5) - 1  # Normalize the image array

        # Predict the class
        prediction = model.predict(image_array)
        index = np.argmax(prediction)
        class_name = class_names[index]
        confidence_score = prediction[0][index]

        # Print prediction and confidence score
        print("Class:", class_name.strip(), end=" ")
        print("Confidence Score:", str(np.round(confidence_score * 100))[:-2], "%")

def greyCheck(img,width,height):
    greyPixels = 0
    for j in range(height):
        for i in range (width):
            (r,g,b) = img[i,j]
            if (r < 170) and (g < 170) and (b < 170):
                greyPixels += 1
    # print(greyPixels)
    return greyPixels

def objectCheck():
    # Grab the camera's image
        ret, image = camera.read()
        if not ret:
            print("Error: Failed to capture image from camera.")

        # Resize the raw image to (224, 224) pixels
        cropped_image = crop_image_by_size(image)
        image_resized = cv2.resize(cropped_image, (224, 224), interpolation=cv2.INTER_AREA)

        # Show the image in a window
       # cv2.imshow("Webcam Image", image_resized)

        # Preprocess the image for the model
        # image_array = np.asarray(image_resized, dtype=np.float32).reshape(1, 224, 224, 3)
        # image_array = (image_array / 127.5) - 1  # Normalize the image array

        # Predict the class
        return greyCheck(image_resized,224,224) > 2600
        # print(num_grey)
        # Print prediction and confidence score
        

board = Arduino("COM3")
it = util.Iterator(board)
it.start()

board.digital[7].mode = SERVO
board.digital[7].write(180)
try:
    while True:
        if(objectCheck()):
            time.sleep(1)
            catScrew()
            board.digital[7].write(0)
            time.sleep(.5)
            board.digital[7].write(180)
            time.sleep(.5)

        time.sleep(1/5)

        keyboard_input = cv2.waitKey(1)
        if keyboard_input == 27:
            break

except KeyboardInterrupt:
    print("Interrupted by user.")

finally:
    # Release resources
    camera.release()
    cv2.destroyAllWindows()
