import tensorflow as tf
import matplotlib.pyplot as plt
import random
import numpy as np

fashion_mnist = tf.keras.datasets.fashion_mnist
(train_images, train_labels), (test_images, test_labels) = fashion_mnist.load_data()
train_images = train_images / 255.0

categories = {
    'upper_body': [0, 2, 3, 4, 6],
    'lower_body': [1],
    'footwear': [5, 7, 9]
}

def get_random_outfit():
    upper_body_images = []
    lower_body_images = []
    footwear_images = []

    for i in range(len(train_labels)):
        if train_labels[i] in categories['upper_body']:
            upper_body_images.append(train_images[i])
        elif train_labels[i] in categories['lower_body']:
            lower_body_images.append(train_images[i])
        elif train_labels[i] in categories['footwear']:
            footwear_images.append(train_images[i])

    upper_body_image = random.choice(upper_body_images) if upper_body_images else None
    lower_body_image = random.choice(lower_body_images) if lower_body_images else None
    footwear_image = random.choice(footwear_images) if footwear_images else None

    return upper_body_image, lower_body_image, footwear_image

def plot_outfit(upper_body_img, lower_body_img, footwear_img):
    plt.figure(figsize=(10, 5))
    plt.subplot(1, 3, 1)
    plt.imshow(upper_body_img, cmap='gray')
    plt.title('Верхняя одежда')
    plt.axis('off')
    
    plt.subplot(1, 3, 2)
    plt.imshow(lower_body_img, cmap='gray')
    plt.title('Нижняя одежда')
    plt.axis('off')
    
    plt.subplot(1, 3, 3)
    plt.imshow(footwear_img, cmap='gray')
    plt.title('Обувь')
    plt.axis('off')
    
    # Save the figure to a file
    plt.tight_layout()
    plt.savefig('OPD2/static/outfit.png')  # Save to static folder
    plt.close()