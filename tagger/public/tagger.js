show('initializing...');

var VIDEO_PADDING = 75
var ongoingTouches = [];
var _currFrameIdx = 0;
var _frameImages = [];
var _overlayCanvas = document.getElementById('canvas')
var _videoCanvas = document.getElementById('img')
var _tracks = []
var _currTrackIdx = 0
var _currVideoId = 'video-31-p_09'

function getNextVideo(cb) {
  $.get('/next-video', {}, function (data) {
    cb(data.videoId, data.images);
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
    show('Done!')
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

function addTrack() {
  _tracks.push(new Array(_frameImages.length))
  _currTrackIdx += 1
  var nextTrackId = _tracks.length
  $('#tracks-list').append(`<li>Track ${nextTrackId}</li>`)
  alert('New track created.')
}

function saveTrack() {
  var tracksData = _tracks.map(function (track) {
    return track.map(function (rect) {
      return {
        x: rect.x + VIDEO_PADDING,
        y: rect.y + VIDEO_PADDING,
        w: rect.w,
        h: rect.h
      }
    })
  })
  $.ajax({
    type: 'POST',
    url: '/save/' + _currVideoId,
    data: JSON.stringify({tracks: tracksData}),
    dataType: 'json',
    contentType: 'application/json; charset=utf-8',
    success: function (data) {
      if (data.success) {
        alert('Track saved!')
      } else {
        alert('ERROR: track was not saved.')
      }
    }
  });
}

function trimStart() {
  for (var i = _currFrameIdx; i >= 0; i--) {
    _tracks[_currTrackIdx][i] = undefined
  }
  alert('Trimmed until start.')
}

function trimEnd() {
  for (var i = _currFrameIdx; i < _frameImages.length; i++) {
    _tracks[_currTrackIdx][i] = undefined
  }
  alert('Trimmed until end.')
}

function startup() {
  var overlayCtx = _overlayCanvas.getContext('2d')
  overlayCtx.canvas.width = window.innerWidth
  overlayCtx.canvas.height = window.innerHeight
  var videoCtx = _videoCanvas.getContext('2d')
  videoCtx.canvas.width = window.innerWidth
  videoCtx.canvas.height = window.innerHeight

  var el = document.getElementById('img')
  var ctx = el.getContext("2d");

  show('Loading images...')
  getNextVideo(function (videoId, imageURLs) {
    _currVideoId = videoId
    console.log(imageURLs)
    loadImages(_.reverse(imageURLs), function (images) {
      _frameImages = images;
      window.images = images;
      // ctx.drawImage(images[0], 0, 0)
      // document.getElementById('img').src = images[0].src;
      _tracks.push(new Array(_frameImages.length))
      renderFrame(0)
      console.log('image', images[0]);
      initialize();
    }, [])
  })
}

var slider = document.getElementById('slider')
var _playInterval = null;

function drawTrackedRects() {
  var ctx = _videoCanvas.getContext('2d')
  for (var i = 0; i < _tracks.length; i++) {
    if (_tracks[i][_currFrameIdx] && (ongoingTouches.length < 2)) {
      var rect = _tracks[i][_currFrameIdx]
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.35)'
      ctx.strokeRect(rect.x, rect.y, rect.w, rect.h)
    }
  }
}

function renderFrame(idx) {
  if (idx >= _frameImages.length) {
    return;
  }
  var el = document.getElementById('img')
  var ctx = el.getContext("2d");
  ctx.drawImage(_frameImages[idx], VIDEO_PADDING, VIDEO_PADDING);
  drawTrackedRects()
}

var _playing = false
var _BEAT = 25;
window._speed = 125;
window._delta = 0;

var _accelInterval;

function initPlayer() {
  _playInterval = window.setInterval(function () {
    if (_playing && (window._delta >= window._speed)) {
      window._delta = 0;
      renderFrame(_currFrameIdx++)
    } else {
      window._delta += _BEAT;
    }
    show(window._speed)
  }, _BEAT);
}

function startPlaying(ms) {
  window._speed = ms
  _playing = true
}

function stopPlaying() {
  _playing = false
}

function initialize() {
  $('#add-button').on('click', addTrack)
  $('#save-button').on('click', saveTrack)
  $('#trim-start-button').on('click', trimStart)
  $('#trim-end-button').on('click', trimEnd)
  var el = document.getElementsByTagName("canvas")[0];
  el.addEventListener("touchstart", handleStart, false);
  el.addEventListener("touchend", handleEnd, false);
  el.addEventListener("touchcancel", handleCancel, false);
  el.addEventListener("touchmove", handleMove, false);
  slider.oninput = function () {
    show('slider: ' + slider.value)
    _currFrameIdx = slider.value
    // var el = document.getElementById('img')
    // var ctx = el.getContext("2d");
    // ctx.drawImage(_frameImages[_currFrameIdx], 0, 0);
    renderFrame(_currFrameIdx)
  }
  slider.max = _frameImages.length - 1
  slider.value = 0
  show("initialized.");
  initPlayer()
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
    // var color = colorForTouch(touches[i]);
    // ctx.beginPath();
    // ctx.arc(touches[i].pageX, touches[i].pageY, 4, 0, 2 * Math.PI, false);  // a circle at the start
    // ctx.fillStyle = color;
    // ctx.fill();
    // log("touchstart:" + i + ".");
  }

  if (ongoingTouches.length == 2) {
    startPlaying(250)
    _accelInterval = window.setInterval(function () {
      var s = window._speed - 25;
      if (s >= 75) {
        window._speed = s
      } else {
        window._speed = 75
      }
      // show((new Date()).getMilliseconds())
    }, 500)
  }

  // if (ongoingTouches.length == 1) {
  //   _lastOngoingTouchX = ongoingTouches[0].pageX;
  // }
}

var _lastOngoingTouchX = null;

function drawTaggingRect() {
    var overlayCtx = _overlayCanvas.getContext('2d')
    var ctx = overlayCtx;
    // var el = document.getElementsByTagName("canvas")[0];
    // var ctx = el.getContext("2d");
    var PADDING = 15;
    var p1, p2;
    if (ongoingTouches[0].pageX < ongoingTouches[1].pageX) {
      p1 = {x: ongoingTouches[0].pageX, y: ongoingTouches[0].pageY}
      p2 = {x: ongoingTouches[1].pageX, y: ongoingTouches[1].pageY}
    } else {
      p1 = {x: ongoingTouches[1].pageX, y: ongoingTouches[1].pageY}
      p2 = {x: ongoingTouches[0].pageX, y: ongoingTouches[0].pageY}
    }
    // assuming right hand usage
    var orig = {x: p1.x, y: p2.y}
    var w = (p2.x - p1.x);
    var h = (p1.y - p2.y);
    ctx.clearRect(0, 0, overlayCtx.canvas.width, overlayCtx.canvas.height);
    ctx.fillStyle = 'rgba(255, 255, 0, 0.35)'
    ctx.fillRect(orig.x + PADDING, orig.y + PADDING, w - 2*PADDING, h - 2*PADDING);
    // show(`P1=(${p1.x},${p1.y}) P2=(${p2.x}, ${p2.y})`)
    _tracks[_currTrackIdx][_currFrameIdx] = {
      x: orig.x + PADDING,
      y: orig.y + PADDING,
      w: w - 2*PADDING,
      h: h - 2*PADDING
    }
}

function clearTaggingRect() {
    var ctx = _overlayCanvas.getContext('2d')
    ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
}

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
    if (!_lastOngoingTouchX) {
      _lastOngoingTouchX = ongoingTouches[0].pageX;
    }
    var deltaX = ongoingTouches[0].pageX - _lastOngoingTouchX;
    var spd = 1;
    var overlayCtx = _overlayCanvas.getContext('2d')
    if (ongoingTouches[0].pageY > (overlayCtx.canvas.height / 2)) {
      spd = 5;
    }
    _currFrameIdx += (deltaX > 0 ? spd : -spd)
    if (_currFrameIdx < 0) {
      _currFrameIdx = 0;
    } else if (_currFrameIdx >= _frameImages.length) {
      _currFrameIdx = _frameImages.length - 1;
    }
    show('one finger: ' + deltaX);
    // document.getElementById('img').src = _frameImages[_currFrameIdx].src;
    // var el = document.getElementById('img')
    // var ctx = el.getContext("2d");
    // ctx.drawImage(_frameImages[_currFrameIdx], 0, 0);
    renderFrame(_currFrameIdx)
    slider.value = _currFrameIdx
    _lastOngoingTouchX = ongoingTouches[0].pageX
  } else if (ongoingTouches.length == 2) {
    // show('two fingers')
    drawTaggingRect();
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
      // ctx.lineWidth = 4;
      // ctx.fillStyle = color;
      // ctx.beginPath();
      // ctx.moveTo(ongoingTouches[idx].pageX, ongoingTouches[idx].pageY);
      // ctx.lineTo(touches[i].pageX, touches[i].pageY);
      // ctx.fillRect(touches[i].pageX - 4, touches[i].pageY - 4, 8, 8);  // and a square at the end
      ongoingTouches.splice(idx, 1);  // remove it; we're done
    } else {
      log("can't figure out which touch to end");
    }
  }

  if (ongoingTouches.length < 2) {
    stopPlaying();
    window.clearInterval(_accelInterval)
    clearTaggingRect()
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

  if (ongoingTouches.length < 2) {
    stopPlaying();
    window.clearInterval(_accelInterval)
    clearTaggingRect()
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
