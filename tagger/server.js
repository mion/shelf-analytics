const express = require('express')
const app = express()
const fs = require('fs')

SHAN_PATH = '/Users/gvieira/code/toneto/shan/tagger/public/shan'
VIDS_PATH = '/Users/gvieira/shan-videos'
ANOT_PATH = '/Users/gvieira/shan-annotations'

app.use(express.static('public'))
app.use(express.json())

function readVideoIdsAt(path, cb) {
  fs.readdir(path, function (err, items) {
    if (err) {
      cb(err, null)
    } else {
      var ids = []
      for (var i = 0; i < items.length; i++) {
        var videoId = items[i].split('.')[0]
        ids.push(videoId)
      }
      cb(null, ids)
    }
  })
}

function getUntaggedVideoIds(cb) {
  readVideoIdsAt(VIDS_PATH, function (err, rawVideoIds) {
    if (err) {
      cb(err, null)
    } else {
      readVideoIdsAt(ANOT_PATH, function (err2, taggedVideoIds) {
        if (err2) {
          cb(err2, null)
        } else {
          var untaggedVideoIds = []
          for (var i = 0; i < rawVideoIds.length; i++) {
            if (taggedVideoIds.indexOf(rawVideoIds[i]) == -1) {
              untaggedVideoIds.push(rawVideoIds[i])
            }
          }
          cb(null, untaggedVideoIds)
        }
      })
    }
  })
}

app.get('/next-video', function (req, res) {
  getUntaggedVideoIds(function (err, untaggedVideoIds) {
    if (err) {
      res.json({success: false, error: err})
    } else {
      res.json({success: true, untaggedVideoIds: untaggedVideoIds})
    }
  })
})

app.get('/videos/:id', function (req, res) {
  fs.readdir(SHAN_PATH + '/' + req.params.id + '/frames/low', function (err, items) {
    if (err) {
      res.json({error: err})
    } else {
      res.json({images: items.map((name) => 'shan/' + req.params.id + '/frames/low/' + name)})
    }
  })
})

app.post('/save/:id', function (req, res) {
  console.log('content-type', req.get('Content-type'))
  console.log('Body for video ID ' + req.params.id)
  console.log(req.body)
  if (req.body.tracks && req.body.tracks.length > 0) {
    fs.writeFile(ANOT_PATH + '/' + req.params.id + '.json', JSON.stringify(req.body), 'utf8', function (err) {
      if (err) {
        res.json({success: false, error: err})
      } else {
        res.json({success: true})
      }
    })
  } else {
    res.json({success: false, error: 'empty track payload'})
  }
})

app.listen(3600, () => console.log('Example app listening on port 3600!'))
