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
//var PICTURE_POST_URL = "https://steam-1111.appspot.com/postpic/"

const LABEL_DETECTION = 'LABEL_DETECTION';
const TEXT_DETECTION = 'TEXT_DETECTION';

class LabelPictureApp extends Component {
  constructor(props) {
      super(props);
      this.state = {
          is_loading: false,
      };
  }

  render() {
    console.log("render called");
    var UI_part;
    if (this.state.is_loading) {
        UI_part = (
            <View style={styles.container}>
                <Text style={styles.capture}>Loading...</Text>
            </View>
        );
    } else {
        UI_part = (
            <View>
                <TouchableHighlight onPress={() => { this.takeAndPostPicture(TEXT_DETECTION) }}>
                    <Text style={styles.capture}>Read Text</Text>
                </TouchableHighlight>

                <TouchableHighlight onPress={() => { this.takeAndPostPicture(LABEL_DETECTION) }}>
                    <Text style={styles.capture}>Label Pic</Text>
                </TouchableHighlight>
            </View>
        );
    }

    return (
      <View style={styles.container}>
        <Camera
          ref={(cam) => {
            this.camera = cam;
          }}
          style={styles.preview}
          //captureTarget={Camera.constants.CaptureTarget.disk}
          captureTarget={Camera.constants.CaptureTarget.temp}
          aspect={Camera.constants.Aspect.Fill}>

          {UI_part}

        </Camera>
      </View>
    );
  }

  takePicture() {
    throw "deprecated";
    this.camera.capture()
      .then((data) => console.log(data))
      .catch(err => console.error(err));
  }

  setNotLoading() {
      this.setState({is_loading: false});
  }

  takeAndPostPicture(detection_type) {
      this.setState({is_loading: true});
      this.camera.capture()
        .then((data) => {
            var request_object = {method: 'POST', body: data};

            var photo = {
                uri: data,
                type: 'image/jpeg',
                name: 'photo.jpg',
            };
            var body = new FormData();

            body.append('photo', photo);
            body.append('detection_type', detection_type);

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
                    this.setNotLoading();
                    return;
                }
                if (!xhr.responseText) {
                    AlertIOS.alert(
                        'Upload failed',
                        'No response payload.'
                    );
                    this.setNotLoading();
                    return;
                }
                console.log("we got a non-error back back, it may or may not have the final result");
                console.log(xhr);
                var response_obj = JSON.parse(xhr.responseText);
                console.log(response_obj);
                if (response_obj.success) {
                    this.setNotLoading();
                    var best_label = response_obj.best_label;
                    AlertIOS.alert(
                        'Nice pic!',
                        best_label
                    );
                }
            };


            //console.log("we got something back from server");
            //console.log(xhr);
            //console.log(xhr);
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
