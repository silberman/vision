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

            var post_info = {
                method: 'POST',
                body: body,
            }

            fetch(PICTURE_POST_URL, post_info)
              .then((response) => response.json())
              .then((response_info) => {
                  console.log(response_info);
                  if (response_info.success) {
                      this.setNotLoading();
                      AlertIOS.alert(
                          'Nice pic!',
                          response_info.best_label
                      );
                  } else {
                      console.warn("response_obj with success false or missing");
                  }
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
