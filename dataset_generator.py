import os
from pre_process import blur_image, rotate_image, add_salt_and_pepper_noise
from cv2 import cv2

# Mexer nesses parâmetros
path = 'dataset/portrait'
variation = 5
output_path = 'dataset/'

# Não mexer 
output_path = output_path + '/' + path.split('/')[-1]

if not os.path.exists(output_path):
    os.mkdir(output_path)

for image_name in os.listdir(path):
    image_path = os.path.join(path, image_name)
    if os.path.isfile(image_path):

        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        for i in range(1, variation + 1):
            blurred = blur_image(image, i)
            rotated = rotate_image(image, i)
            noised = add_salt_and_pepper_noise(image, i)

            blurred_folder = output_path + '-blur-' + str(i)
            rotated_folder = output_path + '-rotation-' + str(i)
            noised_folder = output_path + '-noise-' + str(i)

            if not os.path.exists(blurred_folder):
                os.mkdir(blurred_folder)
                os.mkdir(rotated_folder)
                os.mkdir(noised_folder)
            
            cv2.imwrite(os.path.join(rotated_folder, image_name), rotated)
            cv2.imwrite(os.path.join(noised_folder, image_name), noised)
            blurred.save(os.path.join(blurred_folder, image_name))

