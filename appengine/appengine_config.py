"""
From
https://cloud.google.com/appengine/docs/python/tools/libraries27

When adding a library that appengine needs, we should add it to /vision/requirements.txt,
then

(vision)~/vision$ pip install -t appengine/lib -r requirements.txt
"""


from google.appengine.ext import vendor
import os

# Add any libraries installed in the "lib" folder.
vendor.add(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib'))
