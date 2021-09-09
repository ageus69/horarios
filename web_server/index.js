const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000
app.use(express.static('./build'))

const server = app.listen(PORT, function () {
  console.log('Web server at port' + PORT.toString());
});