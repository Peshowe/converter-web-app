let myInput = document.getElementById('input_text');
let convertedContainer = document.getElementById("convertedContainer");
let convertButton = document.getElementById('convert_button');
let copyButton = document.getElementById('copy_button');
let newConvertButton = document.getElementById('new_button');
let loadingGif = document.getElementById('loading_gif');
let easterEgg = document.getElementById('easter_egg');
let themeButton1 = document.getElementById('theme_button');
let themeButton2 = document.getElementById('theme_icon');

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

    if (val.match(/нощь?та\s*на\s*26\s*-?\s*(?:ти)?\s*февруарий?\s*1945/i)) {
      easterEgg.hidden = false;
    }

    //disable the input while converting
    myInput.hidden = true;
    convertButton.hidden = true;

    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
      if (this.readyState == 4 && this.status == 200) {
        //put the converted text in the second form
        convertedContainer.innerHTML = highlightText(val, this.response['text']);

        converting_in_process = false; //done!

        //hide loading gif and show output box
        loadingGif.hidden = true;
        convertedContainer.hidden = false;
        newConvertButton.hidden = false;
        copyButton.hidden = false;
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


//copy the converted text to the user's clipboard
function copyToClipboard() {
  function animateYatYus() {
    $('#yatyus').show();
    $('#yatyus span').css({
      fontSize: "5%",
      opacity: 0.5
    })
        .animate({
          fontSize: "100%"
        }, 300, function () {
          $(this).animate({opacity: 0}, function () {
            $('#yatyus').hide();
          });
        });
  }

  animateYatYus();
  
  /* Select, copy and unselect the div */
  convertedContainer.contentEditable = 'true';
  convertedContainer.focus();
  document.execCommand('SelectAll');
  document.execCommand("Copy", false, null);
  document.execCommand('Unselect');
  convertedContainer.contentEditable = 'false';
}

function resetConvert() {
  convertedContainer.hidden = true;
  convertedContainer.scrollTop = 0;
  myInput.hidden = false;
  convertButton.hidden = false;
  newConvertButton.hidden = true;
  copyButton.hidden = true;
}

function initTheme() {
  let theme = localStorage.getItem('theme');
  if (!theme) {
    if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      theme = 'dark';
    } else {
      theme = 'light';
    }
  }
  setTheme(theme);
}

function setTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  if (theme === 'dark') {
    themeButton1.innerText = 'Свѣтълъ режимъ';
    themeButton2.innerText = 'Свѣтло';
  } else {
    themeButton1.innerText = 'Тъменъ режимъ';
    themeButton2.innerText = 'Тъмно';
  }
  localStorage.setItem('theme', theme);
}

function getTheme() {
  return document.documentElement.getAttribute('data-theme');
}

function toggleTheme() {
  setTheme(getTheme() === 'dark' ? 'light' : 'dark');
}

function highlightText(a, b) {
  function highlightWord(a, b) {
    if (b.length < a.length) {
      return highlightSingle(b);
    }

    let diff = patienceDiffPlus(a.split(""), b.split(""));

    return diff.lines
        .filter(x => x.bIndex >= 0)
        .map(x => {
          let c = x.line;
          if (x.aIndex < 0) {
            c = highlightSingle(c);
          }
          return c;
        })
        .join('');
  }

  function highlightSingle(x) {
    return '<span class="hi">' + x + '</span>';
  }

  if (!b) {
    return '';
  }
  let wordsA = a.match(/([\u0400-\u04FF]+|[^\u0400-\u04FF]+)/g);
  let wordsB = b.match(/([\u0400-\u04FF]+|[^\u0400-\u04FF]+)/g);
  if (wordsA.length !== wordsB.length) {
    return b;
  }

  let words = [];
  for (let i = 0; i < wordsA.length; i++) {
    if (wordsB[i].match(/^[\u0400-\u04FF]/)) {
      words.push(highlightWord(wordsA[i], wordsB[i]));
    } else {
      words.push(wordsB[i].replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;'));
    }
  }

  return words.join('');
}

initTheme();
