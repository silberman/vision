
import datetime
import json
import httplib2
import logging
import os
import time
import webapp2

from gcloud import storage
from googleapiclient import discovery # for vision API
from oauth2client.client import GoogleCredentials # for vision API

# detection types available from google vision API:
LABEL_DETECTION = 'LABEL_DETECTION'
TEXT_DETECTION = 'TEXT_DETECTION'
FACE_DETECTION = 'FACE_DETECTION'
LANDMARK_DETECTION = 'LANDMARK_DETECTION'
LOGO_DETECTION = 'LOGO_DETECTION'
SAFE_SEARCH_DETECTION = 'SAFE_SEARCH_DETECTION'
IMAGE_PROPERTIES = 'IMAGE_PROPERTIES'

# The google vision API will return lists of annotations for each detection_type
# of 0 - the num we ask for.  The key in their response dicts are:
# ie, asking for 1 label will get something like:
# {u'responses': [{u'labelAnnotations': [{u'mid': u'/m/0n0j', u'score': 0.67856497, u'description': u'area'}]}]}
ANNOTATION_NAME_FOR_DETECTION_TYPE = {
    LABEL_DETECTION: 'labelAnnotations',
    TEXT_DETECTION: 'textAnnotations',
}

ACCEPTED_DETECTION_TYPES = set([LABEL_DETECTION, TEXT_DETECTION])

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World from appengine!')

class TestHandler(webapp2.RequestHandler):
    """
    Useful for testing.  Prints out request arguments and their value's size, and returns
    some success json.
    """
    def post(self):
        for key_index, key in enumerate(self.request.arguments()):
            value = self.request.get(key)
            print key_index, key, len(value), type(value)

        self.response.content_type = 'application/json'
        response_obj = dict(success=True, best_label="test!")
        self.response.write(json.dumps(response_obj))

class PostPictureHandler(webapp2.RequestHandler):
    """
    Receives POSTs of photos/label-requests from the app, returning data gathered from the google
    vision API.
    """
    def post(self):
        for key_index, key in enumerate(self.request.arguments()):
            value = self.request.get(key)
            print key_index, key, len(value), type(value)

        photo_data = self.request.get('photo')
        detection_type = self.request.get('detection_type')
        assert detection_type in ACCEPTED_DETECTION_TYPES

        # Save the data to a google storage bucket
        gs_location = write_photo_via_gcloud_storage(photo_data)

        # get the vision api result
        best_label = get_best_label(gs_location=gs_location, detection_type=detection_type)

        self.response.content_type = 'application/json'
        if best_label is None:
            response_obj = dict(success=False)
        else:
            response_obj = dict(success=True, best_label=best_label)
        print response_obj
        self.response.write(json.dumps(response_obj))

def _safe_filename(filename):
    """
    Generates a safe filename that is unlikely to collide with existing objects
    in Google Cloud Storage.
    ``filename.ext`` is transformed into ``filename-YYYY-MM-DD-HHMMSS.ext``
    """
    date = datetime.datetime.utcnow().strftime("%Y-%m-%d-%H%M%S")
    basename, extension = filename.rsplit('.', 1)
    return "{0}-{1}.{2}".format(basename, date, extension)

def write_photo_via_gcloud_storage(photo_data):
    client = storage.Client(project='steam-1111')
    base_filename = "testfilename.jpg"
    safe_filename = _safe_filename(base_filename)
    bucket_name = 'steam-1111.appspot.com'
    bucket = client.get_bucket(bucket_name)
    content_type = "image/jpeg"
    blob = bucket.blob(safe_filename)
    blob.upload_from_string(photo_data, content_type=content_type)
    gs_location = gs_location_from_bucket_and_filename(bucket_name, safe_filename)
    return gs_location

def gs_location_from_bucket_and_filename(bucket_name, filename):
    return "gs://%s/%s" % (bucket_name, filename)

def get_vision_service():
    DISCOVERY_URL='https://{api}.googleapis.com/$discovery/rest?version={apiVersion}'
    credentials = GoogleCredentials.get_application_default().create_scoped(
        ['https://www.googleapis.com/auth/cloud-platform'])
    return discovery.build('vision', 'v1', credentials=credentials, discoveryServiceUrl=DISCOVERY_URL)

def get_best_label(filename_with_bucket=None, gs_location=None, detection_type=LABEL_DETECTION):
    '''Run a label request on a single image'''
    assert filename_with_bucket or gs_location
    service = get_vision_service()

    if gs_location is None:
        # backward compatibility
        assert filename_with_bucket is not None
        image_uri = "gs:/%s" % (filename_with_bucket)
        print "image_uri:", image_uri
    else:
        image_uri = gs_location

    service_request = service.images().annotate(
      body={
        'requests': [{
          'image': {
            "source": {
                "gcsImageUri": image_uri,
            },
           },
          'features': [{
            'type': detection_type,
            'maxResults': 1,
           }]
         }]
      })
    responses = service_request.execute()
    print "*" * 50
    print responses
    print '*' * 50

    # We are only sending 1, so we only expect 1 response (even if it's an error)
    response = responses['responses'][0]
    if 'error' in response:
        logging.error(response)
        return None

    # For now we just return top top 1 of the single detection_type. We may want the output
    # to be larger, in fact should perhaps just have the frontend deal directly with the output
    # from google
    assert detection_type in ANNOTATION_NAME_FOR_DETECTION_TYPE
    annotation_name = ANNOTATION_NAME_FOR_DETECTION_TYPE[detection_type]
    best_label = response[annotation_name][0]['description']
    return best_label

urls = [
    ('/', MainPage),
    ('/testpostpic/', TestHandler),
    ('/postpic/', PostPictureHandler),
]

app = webapp2.WSGIApplication(urls, debug=True)

def main():
    # Set the logging level in the main function
    # See the section on <a href="/appengine/docs/python/#Python_App_caching">Requests and App Caching</a> for information on how
    # App Engine reuses your request handlers when you specify a main function
    logging.getLogger().setLevel(logging.DEBUG)
    webapp.util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
