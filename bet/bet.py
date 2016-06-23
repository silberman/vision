#!/usr/bin/python

import argparse
import base64
import json
import os
import requests
import subprocess
import sys

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(THIS_DIR, 'data')

# You need to create a browser key credential to be able to run this.
# In gcloud console (console.cloud.google.com), do:
# API Manager -> Credentials -> Create credentials -> API key -> Browser key
# Then set the big string they give you as an environment variable called "VISION_BROWSER_KEY",
# with
GOOGLE_BROWSER_KEY = os.environ.get("VISION_BROWSER_KEY", "")
if not GOOGLE_BROWSER_KEY:
    raise ValueError("Missing VISION_BROWSER_KEY environment variable required to run.  See comment")

BASE_GOOGLE_IMAGES_API_URL = 'https://vision.googleapis.com/v1/images:annotate?key=%s'

ALL_DETECTION_TYPES = [
   'LABEL_DETECTION',
   'FACE_DETECTION',
   'LANDMARK_DETECTION',
   'LOGO_DETECTION',
   'TEXT_DETECTION',
   'SAFE_SEARCH_DETECTION',
   'IMAGE_PROPERTIES',
]

DEFAULT_DETECTION_TYPES = [
   'LABEL_DETECTION',
]

def identify_image_from_file(image_full_filename, max_results=10, detection_types=None):
    if detection_types is None:
        detection_types = DEFAULT_DETECTION_TYPES

    with open(image_full_filename, 'rb') as image:
      image_content = base64.b64encode(image.read())

    # prepare the json to send to the api
    image_content_object = dict(content=image_content)
    features_list = [dict(type=detection_type, maxResults=max_results) for detection_type in detection_types]
    request = dict(image=image_content_object, features=features_list)
    full_requests_to_json = dict(requests=[request])
    json_string = json.dumps(full_requests_to_json)

    # Write out the json request to a file
    image_basename = os.path.basename(image_full_filename.split('.')[0])
    json_partial_filename = "json_request_%s.json" % image_basename
    json_full_filename = os.path.join(DATA_DIR, json_partial_filename)
    with open(json_full_filename, 'w') as json_file:
        json_file.write(json_string)

    # Read in that json file as binary data
    json_file_binary_data = open(json_full_filename, 'rb').read()
    response = requests.post(url=BASE_GOOGLE_IMAGES_API_URL % GOOGLE_BROWSER_KEY,
                             data=json_file_binary_data,
                             headers={'Content-Type': 'application/json'})

    if response.status_code != 200:
        print "Failed, with status code:", response.status_code
        return

    # Got a response, so write it to file
    response_partial_filename = "results_%s.json" % image_basename
    response_full_filename = os.path.join(DATA_DIR, response_partial_filename)
    with open(response_full_filename, 'w') as response_file:
        response_file.write(response.text)

    print response.text
    print "Wrote:", json_full_filename
    print "Wrote:", response_full_filename

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
      'image_file', help="The image you'd like to label.")
    args = parser.parse_args()

    if THIS_DIR in args.image_file:
        image_full_filename = args.image_file
    else:
        image_full_filename = os.path.join(THIS_DIR, args.image_file)

    identify_image_from_file(image_full_filename)
