from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import json
from time import sleep

app = FastAPI()

origins = [
    "http://localhost:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

messages_store = dict()

def init_messages(convo_id: int) -> list[dict[str, str]]:
    messages = [
        {"role": "user", "content": f"This is a prompt for convo {convo_id}..."},
        {"role": "agent", "content": f"This is a response for convo {convo_id}..."},
        {"role": "user", "content": f"This is another prompt for convo {convo_id}..."},
        {"role": "agent", "content": f"This is a response for convo {convo_id}..."},
    ]
    return messages

@app.get("/")
def read_root():
    return {"Hello": "World!"}

@app.get("/messages/{convo_id}")
def read_messages(convo_id: int):
    messages = messages_store.get(convo_id)
    if(not messages):
        messages = init_messages(convo_id=convo_id)
        messages_store[convo_id] = messages
    return messages

@app.websocket("/send/{convo_id}")
async def send_endpoint(websocket: WebSocket, convo_id: int):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        msg_received = json.loads(data)

        messages = read_messages(convo_id=convo_id)
        messages.append(msg_received)

        msg_send = {"role": "agent", "content": "This is a websocket response..."}
        sleep(2)
        messages.append(msg_send)

        await websocket.send_text(json.dumps(msg_send))

