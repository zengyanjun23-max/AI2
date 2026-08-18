import base64
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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


@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
  if not client:
    return {"reply": "錯誤：未設定 GEMINI_API_KEY。"}

  try:
    contents = []

    if request.image:
      image_bytes = base64.b64decode(request.image)
      contents.append(
          types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
      )

    prompt_text = (
        f"Please respond exclusively in {request.language}. "
        f"{request.message}"
    )
    contents.append(prompt_text)

    response = client.models.generate_content(
        model="gemini-3.6-flash", contents=contents
    )
    return {"reply": response.text}
  except Exception as e:
    return {"reply": f"請求失敗：{str(e)}"}
