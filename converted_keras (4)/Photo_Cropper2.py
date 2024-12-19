import os
import cv2
import math

# Define paths
input_folder = r'C:\Users\phamf\Downloads\Screw_Photos_New'
output_folder = r'C:\Users\phamf\Downloads\Screw_Photos_New_Cropped'

# Ensure output folder exists
os.makedirs(output_folder, exist_ok=True)

# Define crop dimensions (width and height)
crop_width = 350  # Width of the cropped image
crop_height = 350  # Height of the cropped image

def crop_image_by_size(image_path, save_path):
    """Crop the image to a fixed size from the center and save to the specified path."""
    # Load the image
    img = cv2.imread(image_path)
    if img is None:
        print(f"Could not read image: {image_path}")
        return
    
    # Get image dimensions
    img_height, img_width = img.shape[:2]
    
    # Ensure the crop dimensions are valid
    if crop_width > img_width or crop_height > img_height:
        print(f"Crop size is larger than the original image for {image_path}. Skipping.")
        return
    
    # Calculate the center of the image
    center_x, center_y = img_width / (2), img_height / (1.8)

    # Calculate the crop box
    x1 = math.floor(center_x - (crop_width / 2))
    y1 = math.floor(center_y - (crop_height / 2))
    x2 = math.floor(center_x + (crop_width / 2))
    y2 = math.floor(center_y + (crop_height / 2))

    # Perform the crop
    cropped_img = img[y1:y2, x1:x2]

    # Save the cropped image
    cv2.imwrite(save_path, cropped_img)

def process_folder(input_subfolder, output_subfolder):
    """Process images in a subfolder and save cropped versions."""
    os.makedirs(output_subfolder, exist_ok=True)
    for image_name in os.listdir(input_subfolder):
        input_image_path = os.path.join(input_subfolder, image_name)
        output_image_path = os.path.join(output_subfolder, image_name)

        # Check if the file is an image
        if image_name.lower().endswith(('.png', '.jpg', '.jpeg')):
            crop_image_by_size(input_image_path, output_image_path)
        else:
            print(f"Skipped file: {image_name}")

# Iterate through subfolders
for subfolder_name in os.listdir(input_folder):
    input_subfolder_path = os.path.join(input_folder, subfolder_name)
    output_subfolder_path = os.path.join(output_folder, subfolder_name)

    if os.path.isdir(input_subfolder_path):
        process_folder(input_subfolder_path, output_subfolder_path)

print("Cropping complete! All cropped images are saved.")


