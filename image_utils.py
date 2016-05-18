#!/usr/bin/python
"""
Some helper functions dealing with images and image files. Basically a wrapper of PIL

Example usage:

image_format, image_shape, image_mode = get_image_info(image_filename)

width, height = get_image_shape(image_filename)
"""

from PIL import Image


def get_image_info(image_filename):
    """
    Return the given image's format, shape (called size in PIL), and mode
    """
    pil_image = Image.open(image_filename)
    return pil_image.format, pil_image.size, pil_image.mode


def get_image_shape(image_filename):
    # Return (width, height) of the given image.
    pil_image = Image.open(image_filename)
    return pil_image.size
