import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
from pydantic import BaseModel

app = FastAPI()

# 設定 CORS 允許跨域存取
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化 Groq 用戶端（需在 Render 設定環境變數 GROQ_API_KEY）
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


class ChatRequest(BaseModel):
  message: str


@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
  try:
    # 呼叫 Groq API 生成對話
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
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
    return {"reply": f"呼叫 AI 時發生錯誤：{str(e)}"}
