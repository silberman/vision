'use strict';
import React, {
  AlertIOS,
  AppRegistry,
  Component,
  Dimensions,
  StyleSheet,
  Text,
  TouchableHighlight,
  View,
} from 'react-native';
import Camera from 'react-native-camera';

var PICTURE_POST_URL = "http://localhost:8080/postpic/";
//PICTURE_POST_URL = "https://steam-1111.appspot.com/postpic/"

class LabelPictureApp extends Component {
    /**
  constructor(props) {
      super(props);
      this.state = {
          is_uploading = false;
      };
  }
  **/

  render() {
    console.log("render called");
    return (
      <View style={styles.container}>
        <Text>Yooooo</Text>
        <Camera
          ref={(cam) => {
            this.camera = cam;
          }}
          style={styles.preview}
          //captureTarget={Camera.constants.CaptureTarget.disk}
          captureTarget={Camera.constants.CaptureTarget.temp}
          aspect={Camera.constants.Aspect.Fill}>
          <TouchableHighlight onPress={this.takeAndPostPicture.bind(this)}>
            <Text style={styles.capture}>[Snap!]</Text>
          </TouchableHighlight>
        </Camera>
      </View>
    );
  }

  takePicture() {
    console.log("takePicture called");
    this.camera.capture()
      .then((data) => console.log(data))
      .catch(err => console.error(err));
  }

  takeAndPostPicture() {
      console.log("takeAndPostPicture called");
      this.camera.capture()
        .then((data) => {
            console.log("heres the data:", data);
            var request_object = {method: 'POST', body: data};

            var photo = {
                uri: data,
                type: 'image/jpeg',
                name: 'photo.jpg',
            };
            console.log(photo);

            var body = new FormData();

            body.append('authToken', 'secret');
            body.append('photo', photo);
            body.append('title', 'A beautiful photo!');

            console.log(body);

            var xhr = new XMLHttpRequest();

            xhr.open('POST', PICTURE_POST_URL);
            xhr.send(body);

            // need to set xhr onload function, as from:
            // https://github.com/facebook/react-native/blob/2d921eeb7073d0286d13195e2975b344793998b0/Examples/UIExplorer/XHRExample.ios.js
            xhr.onload = () => {
                this.setState({isUploading: false});
                if (xhr.status !== 200) {
                    AlertIOS.alert(
                        'Upload failed',
                        'Expected HTTP 200 OK response, got ' + xhr.status
                    );
                    return;
                }
                if (!xhr.responseText) {
                    AlertIOS.alert(
                        'Upload failed',
                        'No response payload.'
                    );
                    return;
                }
                AlertIOS.alert(
                    'We got something back!',
                    'Not sure what it says though'
                );
            };

            console.log("we got something back from server");
            console.log(xhr);
            //console.log()
            return;
            fetch(PICTURE_POST_URL, request_object)
              .then((response) => response.text())
              .then((responseText) => {
                  console.log("response from POSTing:", responseText);
              })
              .catch((error) => {
                  console.warn(error);
            });
        })
        .catch(err => console.error(err));

  }
}

const styles = StyleSheet.create({
  container: {
    flex: 1
  },
  preview: {
    flex: 1,
    justifyContent: 'flex-end',
    alignItems: 'center',
    height: Dimensions.get('window').height,
    width: Dimensions.get('window').width
  },
  capture: {
    flex: 0,
    backgroundColor: '#fff',
    borderRadius: 5,
    color: '#000',
    padding: 10,
    margin: 40
  }
});

AppRegistry.registerComponent('app', () => LabelPictureApp);
