from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# 跨域資源共享 (CORS) 設定：允許前端 HTML 存取此 API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允許所有來源，正式上線建議指定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 定義前端傳入的 JSON 資料結構
class ChatRequest(BaseModel):
  message: str


# 處理對話請求的 API 路由
@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
  user_message = request.message

  # 這裡呼叫 AI 模型（範例以邏輯回傳示範）
  ai_reply = generate_ai_response(user_message)

  return {"reply": ai_reply}


def generate_ai_response(prompt: str) -> str:
  """此處可對接真實的 AI 模型 (如 OpenAI API、Hugging Face 或 Ollama 本地模型)"""
  return f"收到您的訊息：『{prompt}』。這是一個由 Python 後端產生的 AI 回覆範例！"


if __name__ == "__main__":
  import uvicorn

  # 啟動伺服器，運行於 http://127.0.0.1:8000
  uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
