import tensorflow
import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PIL import Image
import numpy as np

# Load the exported TensorFlow model
model = tensorflow.keras.models.load_model('path_to_your_saved_model')

# Define the folder where the images will be saved
IMAGE_FOLDER = "path_to_image_folder"

# Function to preprocess the image
def preprocess_image(image_path, target_size=(224, 224)):
    img = Image.open(image_path)
    img = img.resize(target_size)
    img = np.array(img)
    img = img / 255.0  # Normalize the image
    img = np.expand_dims(img, axis=0)  # Add batch dimension
    return img

# Function to run the model on the image and check the result
def run_model_on_image(image_path):
    img = preprocess_image(image_path)
    prediction = model.predict(img)
    
    # Assuming your model outputs probabilities or class indices
    predicted_class = np.argmax(prediction, axis=1)  # Modify based on your model's output format
    
    # Example conditions based on the model output
    if predicted_class == 0:  # Assuming 0 represents "cat"
        print(f"Prediction for {image_path}: Cat detected")
    elif predicted_class == 1:  # Assuming 1 represents "dog"
        print(f"Prediction for {image_path}: Dog detected")
    else:
        print(f"Prediction for {image_path}: Unknown object detected")

# Event handler to monitor the folder
class ImageHandler(FileSystemEventHandler):
    def on_created(self, event):
        # When a new file is added to the folder, run the model on it
        if event.is_directory:
            return
        file_path = event.src_path
        if file_path.endswith((".png", ".jpg", ".jpeg")):
            print(f"New image detected: {file_path}")
            run_model_on_image(file_path)

# Function to monitor the folder
def monitor_folder():
    event_handler = ImageHandler()
    observer = Observer()
    observer.schedule(event_handler, IMAGE_FOLDER, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    monitor_folder()