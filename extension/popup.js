chrome.tabs.query(
    {
        currentWindow: true,    // currently focused window
        active: true            // selected tab
    },
    function (foundTabs) {
        if (foundTabs.length > 0) {
            var url = foundTabs[0].url; // <--- this is what you are looking for
            document.getElementById('tags').value = String(url);
        } else {
            // there's no window or no selected tab
        }
    }
);

function init() {
  var apisToLoad;
  var callback = function() {
    if (--apisToLoad == 0) {
      signin(true, userAuthed);
    }
  }

  apisToLoad = 1; // must match number of calls to gapi.client.load()
  gapi.client.load('oauth2', 'v2', callback);
}

function signin(mode, callback) {
  gapi.auth.authorize({client_id: "113661887368.apps.googleusercontent.com",
    scope: "https://www.googleapis.com/auth/plus.me", immediate: mode},
    callback);
}

function userAuthed() {
  var request =
      gapi.client.oauth2.userinfo.get().execute(function(resp) {
    if (!resp.code) {
      // User is signed in, call my Endpoint
      console.log("logged_in");
    }
  });
}

function auth() {
  signin(false, userAuthed);
};
