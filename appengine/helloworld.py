
import json
import webapp2

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
        print self.request.get('key')
        print self.request.get('data')

        print self.request.body
        print self.request.body_file.read()
        self.response.content_type = 'application/json'
        response_obj = {
            'success': True,
            'payload': 'XXX'
        }
        self.response.write(json.dumps(response_obj))


urls = [
    ('/', MainPage),
    ('/postpic/', PostPictureHandler),
]

app = webapp2.WSGIApplication(urls, debug=True)
