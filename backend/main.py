from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
client = OpenAI(api_key=os.getenv("OpenAI_API_KEY"))

CONVERSATIONS_DIR = "conversations"
os.makedirs(CONVERSATIONS_DIR, exist_ok=True)

def get_file_path(file_name: str):
    return os.path.join(CONVERSATIONS_DIR, file_name)

def ensure_conversation_exists(file_name: str):
    if not os.path.exists(CONVERSATIONS_DIR):
        os.makedirs(CONVERSATIONS_DIR)
    path = get_file_path(file_name)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write("Sistema: Nueva conversación iniciada\n")

def create_new_conversation():
    filename = datetime.now().strftime("%Y-%m-%d_%H-%M") + ".txt"
    path = get_file_path(filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write("Sistema: Nueva conversación iniciada\n")
    return filename

def append_to_history(file_name: str, role: str, content: str):
    ensure_conversation_exists(file_name)
    with open(get_file_path(file_name), "a", encoding="utf-8") as f:
        f.write(f"{role}: {content}\n")

def read_history(file_name: str):
    ensure_conversation_exists(file_name)
    with open(get_file_path(file_name), "r", encoding="utf-8") as f:
        return f.read()

@app.post("/upload/")
async def upload_file(file: UploadFile, conversation: str = Form(...)):
    ensure_conversation_exists(conversation)
    content = await file.read()
    text = content.decode("utf-8", errors="ignore")
    append_to_history(conversation, "Sistema", f"Archivo subido: {text[:1000]}...")
    return {"message": "Archivo subido y agregado al historial"}

@app.post("/chat/")
async def chat(message: str = Form(...), conversation: str = Form(...)):
    ensure_conversation_exists(conversation)
    append_to_history(conversation, "Usuario", message)
    history_text = read_history(conversation)

    messages = [{"role": "system", "content": ""}]
    for line in history_text.splitlines():
        if line.startswith("Usuario:"):
            messages.append({"role": "user", "content": line.replace("Usuario: ", "")})
        elif line.startswith("Bot:"):
            messages.append({"role": "assistant", "content": line.replace("Bot: ", "")})
        elif line.startswith("Sistema:"):
            messages.append({"role": "system", "content": line.replace("Sistema: ", "")})

    response = groq_client.chat.completions.create(
        model="gpt-4.1",
        messages=messages,
    )

    bot_reply = response.choices[0].message.content
    append_to_history(conversation, "Bot", bot_reply)

    return {"response": bot_reply}

@app.get("/history/")
async def get_history(conversation: str):
    ensure_conversation_exists(conversation)
    return {"history": read_history(conversation)}

@app.post("/clear/")
async def clear_history(conversation: str = Form(...)):
    path = get_file_path(conversation)
    if os.path.exists(path):
        os.remove(path)

    # Si no quedan archivos, crear uno nuevo
    files = os.listdir(CONVERSATIONS_DIR)
    if not files:
        new_file = create_new_conversation()
        return {"message": "Archivo eliminado, se creó uno nuevo porque no quedaban más", "file": new_file}

    return {"message": "Archivo eliminado"}

@app.post("/new_conversation/")
async def new_conversation():
    new_file = create_new_conversation()
    return {"message": "Nueva conversación creada", "file": new_file}

@app.get("/list_conversations/")
async def list_conversations():
    files = sorted(os.listdir(CONVERSATIONS_DIR))
    if not files:
        files.append(create_new_conversation())
    return {"conversations": files}
