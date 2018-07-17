show('initializing...');

var ongoingTouches = [];

function getImages(cb) {
  $.get('/videos/video-31-p_09', {}, function (data) {
    cb(data.images);
  })
}

function loadImage(path, callback) {
  var image = new Image();
  image.src = '/' + path;
  image.onload = function () {
    callback(image);
    image.style.display = 'none';
  };
}

function loadImages(imageURLS, cb, images) {
  if (imageURLS.length == 0) {
    console.log('Done!')
    cb(images);
  } else {
    var url = imageURLS.pop();
    console.log('Loading: ' + url);
    show('Loading: ' + url);
    loadImage(url, (img) => {
      images.push(img);
      loadImages(imageURLS, cb, images);
    })
  }
}

var _currFrameIdx = 0;
var _frameImages = [];

function startup() {
  var el = document.getElementsByTagName("canvas")[0];
  var ctx = el.getContext("2d");

  show('Loading images...')
  getImages(function (imageURLs) {
    console.log(imageURLs)
    loadImages(imageURLs, function (images) {
      _frameImages = images;
      window.images = images;
      // ctx.drawImage(images[0], 0, 0)
      document.getElementById('img').src = images[0].src;
      console.log('image', images[0]);
      initialize();
    }, [])
  })
}

function initialize() {
  var el = document.getElementsByTagName("canvas")[0];
  el.addEventListener("touchstart", handleStart, false);
  el.addEventListener("touchend", handleEnd, false);
  el.addEventListener("touchcancel", handleCancel, false);
  el.addEventListener("touchmove", handleMove, false);
  log("initialized.");
}

function handleStart(evt) {
  evt.preventDefault();
  log("touchstart.");
  var el = document.getElementsByTagName("canvas")[0];
  var ctx = el.getContext("2d");
  var touches = evt.changedTouches;

  for (var i = 0; i < touches.length; i++) {
    log("touchstart:" + i + "...");
    ongoingTouches.push(copyTouch(touches[i]));
    var color = colorForTouch(touches[i]);
    ctx.beginPath();
    ctx.arc(touches[i].pageX, touches[i].pageY, 4, 0, 2 * Math.PI, false);  // a circle at the start
    ctx.fillStyle = color;
    ctx.fill();
    log("touchstart:" + i + ".");
  }

  if (ongoingTouches.length == 1) {
    _lastOngoingTouchX = ongoingTouches[0].pageX;
  }
}

var _lastOngoingTouchX = null;

function handleMove(evt) {
  evt.preventDefault();
  var el = document.getElementsByTagName("canvas")[0];
  var ctx = el.getContext("2d");
  var touches = evt.changedTouches;

  for (var i = 0; i < touches.length; i++) {
    var color = colorForTouch(touches[i]);
    var idx = ongoingTouchIndexById(touches[i].identifier);

    if (idx >= 0) {
      // log("continuing touch "+idx);
      // ctx.beginPath();
      // log("ctx.moveTo(" + ongoingTouches[idx].pageX + ", " + ongoingTouches[idx].pageY + ");");
      // ctx.moveTo(ongoingTouches[idx].pageX, ongoingTouches[idx].pageY);
      // log("ctx.lineTo(" + touches[i].pageX + ", " + touches[i].pageY + ");");
      // ctx.lineTo(touches[i].pageX, touches[i].pageY);
      // ctx.lineWidth = 4;
      // ctx.strokeStyle = color;
      // ctx.stroke();

      ongoingTouches.splice(idx, 1, copyTouch(touches[i]));  // swap in the new touch record
      // log(".");
    } else {
      log("can't figure out which touch to continue");
    }
  }

  if (ongoingTouches.length == 1) {
    if (_lastOngoingTouchX) {
      var deltaX = ongoingTouches[0].pageX - _lastOngoingTouchX;
      var dx = deltaX / 10; // sensivity
      _currFrameIdx += dx;
      if (_currFrameIdx < 0) {
        _currFrameIdx = 0;
      } else if (_currFrameIdx >= _frameImages.length) {
        _currFrameIdx = _frameImages.length - 1;
      }
      show('one finger: ' + deltaX);
      document.getElementById('img').src = _frameImages[_currFrameIdx].src;
    }
  } else if (ongoingTouches.length == 2) {
    show('two fingers')
    var x = ongoingTouches[0].pageX;
    var y = ongoingTouches[0].pageY;
    var w = (ongoingTouches[1].pageX - x);
    var h = (ongoingTouches[1].pageY - y);
    ctx.clearRect(0, 0, 600, 600);
    ctx.fillRect(x, y, w, h);
    show(`(${x},${y}) ${w}x${h}`)
  } else {
    show('')
  }
}

function handleEnd(evt) {
  evt.preventDefault();
  log("touchend");
  var el = document.getElementsByTagName("canvas")[0];
  var ctx = el.getContext("2d");
  var touches = evt.changedTouches;

  for (var i = 0; i < touches.length; i++) {
    var color = colorForTouch(touches[i]);
    var idx = ongoingTouchIndexById(touches[i].identifier);

    if (idx >= 0) {
      ctx.lineWidth = 4;
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.moveTo(ongoingTouches[idx].pageX, ongoingTouches[idx].pageY);
      ctx.lineTo(touches[i].pageX, touches[i].pageY);
      ctx.fillRect(touches[i].pageX - 4, touches[i].pageY - 4, 8, 8);  // and a square at the end
      ongoingTouches.splice(idx, 1);  // remove it; we're done
    } else {
      log("can't figure out which touch to end");
    }
  }
}

function handleCancel(evt) {
  evt.preventDefault();
  log("touchcancel.");
  var touches = evt.changedTouches;

  for (var i = 0; i < touches.length; i++) {
    var idx = ongoingTouchIndexById(touches[i].identifier);
    ongoingTouches.splice(idx, 1);  // remove it; we're done
  }
}

function colorForTouch(touch) {
  var r = touch.identifier % 16;
  var g = Math.floor(touch.identifier / 3) % 16;
  var b = Math.floor(touch.identifier / 7) % 16;
  r = r.toString(16); // make it a hex digit
  g = g.toString(16); // make it a hex digit
  b = b.toString(16); // make it a hex digit
  var color = "#" + r + g + b;
  log("color for touch with identifier " + touch.identifier + " = " + color);
  return color;
}

function copyTouch(touch) {
  return { identifier: touch.identifier, pageX: touch.pageX, pageY: touch.pageY };
}

function ongoingTouchIndexById(idToFind) {
  for (var i = 0; i < ongoingTouches.length; i++) {
    var id = ongoingTouches[i].identifier;

    if (id == idToFind) {
      return i;
    }
  }
  return -1;    // not found
}

function log(msg) {
  // var p = document.getElementById('log');
  // p.innerHTML = msg + "\n" + p.innerHTML;
  console.log(msg)
}

function show(msg) {
  document.getElementById('log').innerHTML = msg;
}
