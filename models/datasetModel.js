var structure = new mongoose.Schema({
  name: {type: String, required: true},
  description: {type: String, required: false},
  files: [
    {
      minio_id: {type: String, required: true},
      filename: {type: String, required: true}
    }
  ]
})

module.exports = ocrx.model('dataset', structure);