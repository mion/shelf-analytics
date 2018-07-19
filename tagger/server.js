const express = require('express')
const app = express()
const fs = require('fs')

SHAN_PATH = '/Users/gvieira/code/toneto/shan/tagger/public/shan'
ANOT_PATH = '/Users/gvieira/shan-annotations'

app.use(express.static('public'))
app.use(express.json())

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
    fs.writeFile(ANOT_PATH + '/annotated-' + req.params.id + '.json', JSON.stringify(req.body), 'utf8', function (err) {
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
