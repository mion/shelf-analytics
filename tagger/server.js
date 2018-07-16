const express = require('express')
const app = express()
const fs = require('fs')

SHAN_PATH = '/Users/gvieira/code/toneto/shan/tagger/public/shan'

app.use(express.static('public'))

app.get('/videos/:id', function (req, res) {
  fs.readdir(SHAN_PATH + '/' + req.params.id + '/frames/low', function (err, items) {
    if (err) {
      res.json({error: err})
    } else {
      res.json({images: items.map((name) => 'shan/' + req.params.id + '/frames/low/' + name)})
    }
  })
})

app.listen(3600, () => console.log('Example app listening on port 3600!'))
