import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from google import genai
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
  api_key = os.environ.get("GEMINI_API_KEY")

  if not api_key:
    return {"reply": "錯誤：伺服器未設定 GEMINI_API_KEY 環境變數。"}

  try:
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-3.6-flash",  # 已更換為系統建議的最新模型
        contents=request.message,
    )
    return {"reply": response.text}
  except Exception as e:
    return {"reply": f"呼叫 Gemini API 失敗：{str(e)}"}
