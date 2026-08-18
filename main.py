import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
  message: str


@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
  api_key = os.environ.get("GROQ_API_KEY")

  if not api_key:
    return {"reply": "錯誤：伺服器未設定 GROQ_API_KEY 環境變數。"}

  try:
    client = Groq(api_key=api_key)
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",  # 目前 Groq 線上支援的最新模型
        messages=[
            {
                "role": "system",
                "content": "你是一個親切且樂於助人的 AI 繁體中文對話助手。",
            },
            {"role": "user", "content": request.message},
        ],
        temperature=0.7,
    )
    ai_reply = completion.choices[0].message.content
    return {"reply": ai_reply}
  except Exception as e:
    return {"reply": f"呼叫 Groq API 失敗：{str(e)}"}
