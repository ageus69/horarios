import React, {useState} from 'react'
import './index.css'

const socketProtocol = (window.location.protocol === 'https:' ? 'wss:' : 'ws:')
const echoSocketUrl = socketProtocol + '//' + 'ia-server-horarios.herokuapp.com'
//const echoSocketUrl = socketProtocol + '//' + 'localhost:3001'
const mapDias = ['L', 'M', 'I', 'J', 'V', 'S']

function Step1 () {
  const [messageFromServer, setMessageFromServer] = useState('')
  const [isSetMaterias, setIsSetMaterias] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [noMaterias, setNoMaterias] = useState(0)
  const [noEpochs, setNoEpochs] = useState(0)
  const [noHorarios, setNoHorarios] = useState(0)
  const [calendario, setCalendario] = useState(0)
  const [inputs, setInputs] = useState([])
  const [resultados, setResultados] = useState([])
  const [resultadosObjt, setResultadosObjt] = useState([])
  const [socketConst, setSocketConst] = useState(null)

  const handleSubmit = (e) => {
    e.preventDefault()

    if (noMaterias < 2 || noMaterias > 8) {
      alert('No son suficientes materias, seleccione entre 2 y 8')
      return
    }

    for (let i=0; i<noMaterias; i++) {
      if(document.getElementById(`inp${i}`).value === '') {
        alert('Algunos campos no estan llenos')
        return
      }
    }

    if(noEpochs < 1 || noEpochs > 1000) {
      alert('Selecciona de entre 1 a 100 epocas')
      return
    }
    let list = []
    for (let i=0; i<noMaterias; i++) {
      list.push(document.getElementById(`inp${i}`).value)
    }

    setIsSetMaterias(true)
    setIsProcessing(true)

    var socket = new WebSocket(echoSocketUrl, 'echo-protocol');
    socket.onmessage = e => {
      if(e.data.length === 0){
        return
      }
      var data = JSON.parse(e.data)
      if(data['type'] === 'status') {
        setMessageFromServer(data['body'])
      }
      if(data['type'] === 'horario') {
        setNoHorarios(noHorarios + 1) // Add to schedule counter

        let obj = JSON.parse(data['body'])
        obj.id = data['key']
        let auxid = obj.id.toString()

        let arrayHours = []
        for (let i=0; i<(obj.hf-obj.hi); i++) {
          arrayHours.push(obj.hi + i)
        }


        let array01 = [] // Los cuadros que tienen materia
        let array02 = [] // Las rows
        let array04 = [] // Clases para segunda tabla
        let array05 = []

        for (let claseKey in obj.clases) {
          let clase = obj.clases[claseKey]
          let color = '#'+Math.floor(Math.random()*16777215).toString(16)
          for (let diaKey in clase.dias) {
            let dia = clase.dias[diaKey]
            let res = array05.find(elemento => elemento === claseKey)
            if(res){}
            else{
              array05.push(claseKey)
              array04.push((
                <tr style={{backgroundColor: color}}>
                  <td>{claseKey}</td>
                  <td>{clase.nrc}</td>
                  <td>{clase.profe}</td>
                </tr>
              ))
            }
            for (let i=dia.horaI; i<dia.horaF; i++) {
              let key = diaKey + (i+7)
              array01.push([key, <td key={key} style={{backgroundColor: color}}>{claseKey}</td>])
            }
          }
        }
        console.log(array01)

        
        for (let i=0; i<mapDias.length; i++) { // Por cada dia
          let array03 = [] // Los td de la current row
          
          for (let j=obj.hi; j<obj.hf; j++) {
            
            let currentKey = mapDias[i] + j.toString()
            let res = array01.find(elemento => elemento[0] === currentKey)
            console.log(currentKey)
            if(res)  
              array03.push(res[1])
            else
              array03.push(<td key={currentKey}></td>)
          }
          array02.push(array03) // Row based in the current i day          
        }

        setResultados(resultados => [...resultados, 
          <tr key={auxid} align='center'>
            <td>
              <div className='tableTrContainer'>
                <table className='tableSchedule'>
                  <tbody>
                    <tr>
                      <th></th>
                      {arrayHours.map(hour => <td key={hour}>{hour}</td>)}
                    </tr>

                    {mapDias.map((dia, index) => <tr key={dia}>
                        <th>
                          {dia}
                        </th>
                          {array02[index].map(el => el)}
                    </tr>)}
                  </tbody>
                </table>
              </div>
            </td>
            <td>
              <div className='tableTrContainer'>
                <table className='tableSchedule'>
                  <tr>
                    <th>Clase</th>
                    <th>Nrc</th>
                    <th>Profe</th>
                  </tr> 
                  {array04.map(a => a)}
                </table>
              </div>
            </td>
          </tr>
        ])
        
      }
    } 
    socket.onopen = function () {
      socket.send(JSON.stringify({type:'postMaterias', body:list, epochs:noEpochs, cal:calendario}))
    };
    setSocketConst(socket)
  }
  

  if(!isSetMaterias) {
    return (
      <>
        <table className='table'>
          <tbody>
            <tr>
              <th id='HeaderTable' colSpan='4'>
                Horarios APP
              </th>
            </tr>
            
            <tr>
              <th>
                No. Materias
              </th>
              <td>
                <input 
                type='number'
                min='2'
                max='8' 
                value={noMaterias}
                onChange={(e) => {
                  setNoMaterias(e.target.value)
                  const list = []
                  for (let i=0; i<e.target.value; i++) {
                    list.push(<input type='text' id={`inp${i}`} key={i} />)
                  }
                  setInputs(list)
                }}/>
              </td>
            </tr>
            <tr>
              <th>Epochs</th>
              <td>
                <input 
                type='number' 
                id='epcInp'
                value={noEpochs}
                onChange={(e) => setNoEpochs(e.target.value)} />
              </td>
            </tr>
            <tr>
              <th>Calendario</th>
              <td>
                <input 
                type='text' 
                id='epcInp'
                value={calendario}
                onChange={(e) => setCalendario(e.target.value)} />
              </td>
            </tr>
            <tr>
              <th>Claves</th>
              <td>{inputs}</td>
            </tr>
            <tr>
              <th></th>
              <td><button onClick={handleSubmit}>Encontrar horarios</button></td>
            </tr>
          </tbody>
        </table>
      </>
    )
  }
  else if(isProcessing && messageFromServer !== 'finished') {
    return (
      <>
        <table className='table'>
          <tbody>
            <tr>
              <th id='HeaderTable' colSpan='4'>
                Horarios APP proceso
              </th>
            </tr>
            <tr>
              <th>
                Generation
              </th>
              <td>
                {messageFromServer || 0}
              </td>
            </tr>
          </tbody>
        </table>
      </>
    )
  }

  else {
    return (
      <>
        <table className='tableSchedule'>
          <tbody>
            <tr>
              <th id='HeaderTable' colSpan='4'>
                Horarios APP resultados
              </th>
            </tr>
            {resultados}
          </tbody>
        </table> 
      </>
    )
  }
  

}

export default Step1