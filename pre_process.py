from cv2 import cv2
import random
from PIL import Image, ImageFilter

example = 'dataset/29_page9.png'

# expects opencv image
def blur_image(image, intensity):
    image = Image.fromarray(image)
    blurredImage = image.filter(ImageFilter.GaussianBlur(intensity))

    return blurredImage

# expects opencv image
def add_salt_and_pepper_noise(image, intensity):
    row, col = image.shape
    number_of_pixels = intensity * 10000

    def createDot(color):
        for _ in range(number_of_pixels):
            y_coord = random.randint(0, row - 1)
            x_coord = random.randint(0, col - 1)
            image[y_coord][x_coord] = color

    createDot(255)
    createDot(0)

    return image

# expects opencv image
def rotate_image(image, angle):
  (h, w) = (image.shape[0], image.shape[1])
  center = (w // 2, h // 2)
  M = cv2.getRotationMatrix2D(center, angle, 1.0)
  rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

  return rotated
