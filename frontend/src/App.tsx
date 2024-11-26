import { FormEvent, useEffect, useState, useRef } from 'react'
import './App.css'
import axios from 'axios'

interface Message {
  role: string
  content: string
}

function App() {
  const [input, setInput] = useState("")
  const [messages, setMessages] = useState<Array<Message> | null>(null)
  const [inputEnabled, setInputEnabled] = useState(true)
  const [convoID, setConvoID] = useState(0)

  const ws = useRef<WebSocket | null>(null) 
  
  useEffect(() => {
    console.log("App use effect, load websocket")
    const websocket = new WebSocket(`ws://localhost:8000/send/${convoID}`)
    websocket.onopen = () => console.log('ws opened');
    websocket.onclose = () => console.log('ws closed');
    websocket.onmessage = (e: MessageEvent) => {
      const newMessage: Message = JSON.parse(e.data)
      setMessages((prevMessages) => {
        if (prevMessages) {
          return [...prevMessages, newMessage]
        }
        else {
          return [newMessage]
        }
      })
      console.log("Received: ", newMessage)
      setInputEnabled(true)
    }
    ws.current = websocket

    return () => {
      if (websocket.readyState === 1) {
        websocket.close()
      }
    }
  }, [convoID])

  useEffect(() => {
    axios.get(`http://localhost:8000/messages/${convoID}`)
      .then((response) => {
        console.log("Received: ", response.data)
        setMessages(response.data)
      })
      .catch(error => console.log(error))
  }, [convoID])

  function handleSubmit(e: FormEvent) {
    e.preventDefault()

    const newMessage: Message = {role: "user", content: input}
    
    if (ws.current) {
      ws.current.send(JSON.stringify(newMessage))
      setMessages((prevMessages) => {
        if (prevMessages) {
          return [...prevMessages, newMessage]
        }
        else {
          return [newMessage]
        }
      })
      setInput('')
      setInputEnabled(false)
      
      console.log("Sent: ", newMessage)  
    }
    else {
      console.log("No available websocket")
    }
  }

  return (
    <>
      <div>
        <label htmlFor="convoID">Convo ID:</label>
        <input
          type="number"
          name="convoID"
          value={ convoID }
          onChange={ e => setConvoID( parseInt(e.target.value) ) }
          disabled={ !inputEnabled }
        />
      </div>
      <br/>
      <div>        
        {
          messages ?
            messages.map((msg, i) => (
              <div key={ i }>
                <span>{ msg.role }: </span>
                <span>{ msg.content }</span>
              </div>
            ))
            :
            null
        }
      </div>
      <div>
        <form method="post" onSubmit={ handleSubmit } >
          <input name="newMessage" value={ input } onChange={ e => setInput(e.target.value) } disabled={ !inputEnabled }/>
          <button type="submit">Send</button>
        </form>
      </div>
    </>
  )
}

export default App
