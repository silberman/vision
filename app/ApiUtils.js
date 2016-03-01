/**
From http://www.yoniweisbrod.com/network-requests-in-react-native-using-fetch/

The React Native documentation warns us that "Errors thrown by rejected Promises need to be caught,
or they will be swallowed silently", which is true - but it is not the only concern.

The thing is, fetch only returns an error when when there is a network error or when something else
gets in the way of the network request completing. It does not throw an error if your authentication
fails, for instance.

That means that we need to handle HTTP status codes ourself.

fetch usage example:

fetch(PICTURE_POST_URL, post_info)
  .then(ApiUtils.checkStatus)
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

**/
var ApiUtils = {
  checkStatus: function(response) {
    // https://github.com/github/fetch
    if (response.status >= 200 && response.status < 300) {
      return response;
    } else {
      let error = new Error(response.statusText);
      error.response = response;
      throw error;
    }
  }
};

export { ApiUtils as default };
