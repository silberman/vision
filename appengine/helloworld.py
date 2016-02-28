
import json
import httplib2
import logging
import os
import time
import webapp2

import cloudstorage as gcs
from googleapiclient import discovery
from apiclient.discovery import build
from oauth2client.client import GoogleCredentials

class MainPage(webapp2.RequestHandler):
    def get(self):
        print "MainPage get() called"
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World from appengine!')

class PostPictureHandler(webapp2.RequestHandler):
    def post(self):
        print '*' * 50
        print "PostPictureHandler post() called"
        print self.request.arguments()
        print len(self.request.arguments())
        print '*' * 10
        for key_index, key in enumerate(self.request.arguments()):
            value = self.request.get(key)
            print key_index, key, len(value), type(value)


        photo_data = self.request.get('photo')

        filename_created = write_photo(photo_data)
        best_label = get_best_label(filename_created)

        self.response.content_type = 'application/json'

        if best_label is None:
            response_obj = dict(success=False)
        else:
            response_obj = dict(success=True, best_label=best_label)
        print response_obj
        self.response.write(json.dumps(response_obj))


def write_photo(photo_from_POST):
    write_retry_params = gcs.RetryParams(backoff_factor=1.1)

    bucket_name = '/steam-1111.appspot.com'
    filename = "%s/%s_%s.jpg" % (bucket_name, 'fromreactnative', time.time())

    # https://cloud.google.com/storage/docs/reference-headers#xgoogmeta
    gcs_file = gcs.open(filename,
                        'w',
                        content_type='image/jpg',
                        options={},
                        retry_params=write_retry_params)
    gcs_file.write(photo_from_POST)
    gcs_file.close()
    logging.debug("Wrote: %s" % filename)
    return filename

def get_vision_service():
    print "*" * 50
    print "os.environ:", os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    DISCOVERY_URL='https://{api}.googleapis.com/$discovery/rest?version={apiVersion}'
    credentials = GoogleCredentials.get_application_default().create_scoped(
        ['https://www.googleapis.com/auth/cloud-platform'])
    http = httplib2.Http()
    credentials.authorize(http)
    return discovery.build('vision', 'v1', credentials=credentials,
                           discoveryServiceUrl=DISCOVERY_URL)

def get_best_label(filename_with_bucket):
    '''Run a label request on a single image'''
    print "get_best_label called with filename", filename_with_bucket

    service = get_vision_service()
    print "service:", service

    image_uri = "gs:/%s" % (filename_with_bucket)
    print "image_uri:", image_uri

    service_request = service.images().annotate(
      body={
        'requests': [{
          'image': {
            "source": {
                "gcsImageUri": image_uri,
            },
           },
          'features': [{
            'type': 'LABEL_DETECTION',
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
    print response
    if 'error' in response:
        logging.error(response)
        return None

    label = response['labelAnnotations'][0]['description']
    logging.debug('Found label: %s for %s' % (label, filename_with_bucket))
    return label

urls = [
    ('/', MainPage),
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
