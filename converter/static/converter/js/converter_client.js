let myInput = document.getElementById('input_text');
let convertedContainer = document.getElementById("convertedContainer");
let convertButton = document.getElementById('convert_button');
let loadingGif = document.getElementById('loading_gif');

let crsf_token;

function set_crsf(val) {
  crsf_token = val
}

let postInterval;
let seconds_since_last_post = 5;
let post_interval_seconds = 2;
let converting_in_process = false

// This function is passed in an interval that runs it each second after a user submits
// it runs for post_interval_seconds seconds or until the converting is done 
let click_interval_func = function () {
  if (!converting_in_process && (seconds_since_last_post > post_interval_seconds)) {
    //enable the convert button back on and clear the interval
    convertButton.disabled = false;
    clearInterval(postInterval);
  } else {
    seconds_since_last_post++;
  }
}

// Send text to server to convert and populate textbox
function convert() {
  // post only every post_interval seconds
  if (!converting_in_process && (seconds_since_last_post > post_interval_seconds)) {
    converting_in_process = true;

    //show loading gif and hide output box
    loadingGif.hidden = false;
    convertedContainer.hidden = true;
    clearInterval(postInterval);
    seconds_since_last_post = 0;

    //disable button for 3 seconds (the function in the interval will enable it)
    convertButton.disabled = true;

    //start the interval that will eventually allow the user to post again
    postInterval = setInterval(click_interval_func, 1000);

    var val = myInput.value;

    //disable the input while converting
    myInput.disabled = true;

    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
      if (this.readyState == 4 && this.status == 200) {
        //put the converted text in the second form
        convertedContainer.innerHTML = this.response['text'];

        //enable input back on
        myInput.disabled = false;
        converting_in_process = false; //done!

        //hide loading gif and show output box
        loadingGif.hidden = true;
        convertedContainer.hidden = false;
      } else if (this.status >= 400) {
        //something went wrong, so put a generic hardcoded error message
        convertedContainer.innerHTML = "Възникна грѣшка... прѣзаредѣте страницата";

        //hide loading gif and show output box
        loadingGif.hidden = true;
        convertedContainer.hidden = false;
      }
    };

    xhttp.responseType = 'json';
    xhttp.open("POST", "convert_text/", true);
    xhttp.setRequestHeader("X-CSRFToken", crsf_token);
    xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");

    xhttp.send(encodeURIComponent('input_text') + '=' + encodeURIComponent(val));
  }
}



// a sad attempt at enabling dark mode functionality
// function toggleDarkMode() {
//   var element = document.body;
//   element.classList.toggle("dark-mode");
//   myInput.classList.toggle("dark-mode");
//   convertedContainer.classList.toggle("dark-mode");
// }