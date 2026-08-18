from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# 跨域資源共享 (CORS) 設定：允許前端 HTML 網頁存取此 API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允許所有來源網域存取
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 定義前端傳入的 JSON 資料格式
class ChatRequest(BaseModel):
  message: str


# 對話 API 路由
@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
  user_message = request.message

  # 呼叫 AI 回應邏輯
  ai_reply = generate_ai_response(user_message)

  return {"reply": ai_reply}


def generate_ai_response(prompt: str) -> str:
  """這是產生 AI 回覆的核心邏輯。

  目前為測試文字，後續可在此處串接 OpenAI API 或其他模型 API。
  """
  return f"收到您的訊息：「{prompt}」。這是由 Python FastAPI 後端回傳的訊息！"


if __name__ == "__main__":
  import uvicorn

  uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
