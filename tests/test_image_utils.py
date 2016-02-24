#!/usr/bin/python
"""
Unittests for image_utils.py
"""

import os
import unittest

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

from image_utils import get_image_info, get_image_shape

class Test_Utils(unittest.TestCase):
    def setUp(self):
        self.image_full_filename_1 = os.path.join(THIS_DIR, 'wide_red_rectangle_640_480.png')

    def test_get_image_info(self):
        image_format, image_shape, image_mode = get_image_info(self.image_full_filename_1)
        self.assertEqual(image_format, 'PNG')
        self.assertEqual(image_shape[0], 640)
        self.assertEqual(image_shape[1], 400)
        self.assertEqual(image_mode, 'RGBA')

    def test_get_image_shape(self):
        width, height = get_image_shape(self.image_full_filename_1)
        self.assertEqual(width, 640)
        self.assertEqual(height, 400)

if __name__ == "__main__":
    unittest.main()
