let myInput = document.getElementById('input_text');
let crsf_token;

function set_crsf(val){
  crsf_token = val
}

let postInterval;
let seconds_since_last_post = 5;
let post_interval_seconds = 3;

// Send text to server to convert and populate textbox
function convert() {
  // post only every post_interval seconds
  if(seconds_since_last_post > post_interval_seconds){

    clearInterval(postInterval);
    seconds_since_last_post = 0;
    postInterval = setInterval(function () {
      seconds_since_last_post++;
    }, 1000);

    var val = myInput.value;

    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
        document.getElementById("convertedContainer").innerHTML = this.response['text'];
      }
    };

    xhttp.responseType = 'json';
    xhttp.open("POST", "convert_text/", true);
    xhttp.setRequestHeader("X-CSRFToken", crsf_token);
    xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");

    xhttp.send(encodeURIComponent('input_text') + '=' + encodeURIComponent(val));
  }
}
