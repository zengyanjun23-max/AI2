import base64
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from google import genai
from google.genai import types
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None


class ChatRequest(BaseModel):
  message: str
  image: str | None = None
  language: str | None = "Traditional Chinese"


@app.get("/")
async def root():
  return {"message": "Server is running properly."}


@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
  if not client:
    return StreamingResponse(
        iter(["錯誤：伺服器未設定 GEMINI_API_KEY。"]), media_type="text/plain"
    )

  contents = []
  if request.image:
    try:
      image_bytes = base64.b64decode(request.image)
      contents.append(
          types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
      )
    except Exception as e:
      print(f"Image parse error: {e}")

  prompt_text = (
      f"Please respond exclusively in {request.language}. {request.message}"
  )
  contents.append(prompt_text)

  def generate_stream():
    try:
      response_stream = client.models.generate_content_stream(
          model="gemini-3.6-flash", contents=contents
      )
      for chunk in response_stream:
        if chunk.text:
          yield chunk.text
    except Exception as e:
      yield f"\n[請求失敗: {str(e)}]"

  return StreamingResponse(generate_stream(), media_type="text/plain")
