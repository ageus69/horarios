const PORT = process.env.PORT || 3001
const express     = require('express')
const {spawn}     = require('child_process')
var expressWs = require('express-ws');
var expressWs = expressWs(express());
var app = expressWs.app;

// environments
app.use(express.static(__dirname + '/public'));
app.use(express.json({limit: '50mb'}));
app.use(express.urlencoded({
  limit: '50mb',
  extended: true
}));

app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Headers', 'Authorization, X-API-KEY, Origin, X-Requested-With, Content-Type, Accept, Access-Control-Allow-Request-Method');
  res.header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE');
  res.header('Allow', 'GET, POST, OPTIONS, PUT, DELETE');
  next();
});

app.listen(PORT, () => {
  console.log('image server listening on' + PORT.toString())
})

app.ws('/', (ws, req) => {
  let queue = []
  console.log('nueva conection')
  ws.on('message', msg => {
    
    var data = JSON.parse(msg)
 
    if(data['type'] == 'postMaterias') {
      const python = spawn('python', ['gaCupos.py', data['body'], parseInt(data['epochs'], 10), data['cal']]);
      
      python.stdout.on('data', (data) => {
        jsonData = {}
        try {
          jsonData = JSON.parse(data.toString())
        } catch (error) {
          console.log(error)
          return
        }
        
        if(jsonData['type'] === 'status'){
          ws.send(data.toString())
        }
        else{
          queue.push(data.toString())
        }
      });

      python.on('close', (code) => {
        console.log(`child porcess close all stdo with code ${code}`);
        queue.forEach(element => {
          ws.send(element)
        });
        ws.send(JSON.stringify({
          'type':'status',
          'body':'finished'
        }))
      });

    }
  })

  ws.on('close', msg => {
    console.log('desconectado')
  })

})