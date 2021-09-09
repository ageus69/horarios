import React, {useEffect, useState} from 'react'
import './index.css'

const socketProtocol = (window.location.protocol === 'https:' ? 'wss:' : 'ws:')
const echoSocketUrl = socketProtocol + '//' + 'ia-server-horarios.herokuapp.com'
let socket

function Step1 () {
  const [messageFromServer, setMessageFromServer] = useState('')
  const [isSetNoMaterias, setIsSetNoMaterias] = useState(false)
  const [isSetMaterias, setIsSetMaterias] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [noMaterias, setNoMaterias] = useState(0)
  const [noEpochs, setNoEpochs] = useState(0)
  const [noHorarios, setNoHorarios] = useState(0)
  const [calendario, setCalendario] = useState(0)
  const [inputs, setInputs] = useState([])
  const [resultados, setResultados] = useState([])
  
  useEffect(() => {
    socket = new WebSocket(echoSocketUrl, 'echo-protocol');
    socket.onmessage = e => {
      if(e.data.length === 0){
        return
      }
      console.log('len', e.data.length)
      console.log('len', e.data)
      console.log('')
      var data = JSON.parse(e.data)
      //console.log(data)
      if(data['type'] === 'status') {
        setMessageFromServer(data['body'])
      }
      if(data['type'] === 'horario') {
        setNoHorarios(noHorarios + 1)
        if(parseInt(data['key']) % 2 === 0) {
          setResultados(resultados => [...resultados, <span className='pairSpan' key={data['key']}>{data['body']}</span>])
        }
        else {
          setResultados(resultados => [...resultados, <span className='nonSpan' key={data['key']}>{data['body']}</span>])
        }
      }
    } 
  }, [])

  const handleSubmit = (e) => {
    e.preventDefault()
    if(noEpochs < 1 || noEpochs > 1000) {
      alert('Selecciona de entre 1 a 100 epocas')
      return
    }
    let list = []
    for (let i=0; i<noMaterias; i++) {
      list.push(document.getElementById(`inp${i}`).value)
    }
    console.log(list)
    setIsSetMaterias(true)
    setIsProcessing(true)
    socket.send(JSON.stringify({type:'postMaterias', body:list, epochs:noEpochs, cal:calendario}))
  }
  

  const handleNoMaterias = (e) => {
    e.preventDefault()
    if(noMaterias < 2 || noMaterias > 8) {
      alert('Selecciona de entre 2 a 8 materias')
      return
    }
    const list = []
    for (let i=0; i<noMaterias; i++) {
      list.push(<input type='text' id={`inp${i}`} key={i} />)
    }
    setInputs(...inputs, list)
    setIsSetNoMaterias(true)
  }

  if(isSetNoMaterias && !isSetMaterias) {
    return (
      <>
        <div>
          <label>Epochs</label>
          <input 
            type='number' 
            id='epcInp'
            value={noEpochs}
            onChange={(e) => setNoEpochs(e.target.value)} />
        </div>
        <div>
          <label>Calendario</label>
          <input 
            type='text' 
            id='epcInp'
            value={calendario}
            onChange={(e) => setCalendario(e.target.value)} />
        </div>
        <div>
          <label>Claves</label>
          {inputs}
        </div>
        <div>
          <button onClick={handleSubmit}>Encontrar horarios</button>
        </div>
      </>
    )
  }

  else if(!isSetMaterias && !isSetNoMaterias) {
    return (
      <>
        <div>
          <label>Cuantas materias vas a agendar? (2 a 8)</label>
          <input 
            type='number' 
            value={noMaterias}
            onChange={(e) => setNoMaterias(e.target.value)}/>
          <button 
            onClick={handleNoMaterias}>OK</button>
        </div>
      </>
    )
  }

  else if(isProcessing && messageFromServer !== 'finished') {
    return (
      <>
        <h1>Generation: {messageFromServer}</h1>
      </>
    )
  }

  else {
    return (
      <>
        <h1>Resultados: </h1>
        {resultados}
      </>
    )
  }
  

}



export default Step1