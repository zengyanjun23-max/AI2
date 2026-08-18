import base64
import os
from fastapi import FastAPI, HTTPException
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


class ChatRequest(BaseModel):
  message: str | None = ""
  image: str | None = None
  language: str | None = "Traditional Chinese"


@app.get("/")
async def root():
  return {"status": "ok"}


@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
  if not api_key:
    raise HTTPException(status_code=500, detail="GEMINI_API_KEY not set")

  client = genai.Client(api_key=api_key)

  contents = []
  if request.image:
    try:
      image_bytes = base64.b64decode(request.image)
      contents.append(
          types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
      )
    except Exception as e:
      print(f"Image decode error: {e}")

  prompt = (
      f"Please reply in {request.language}. {request.message}"
      if request.message
      else f"Please describe this image in {request.language}."
  )
  contents.append(prompt)

  def stream_generator():
    try:
      response = client.models.generate_content_stream(
          model="gemini-3.6-flash", contents=contents
      )
      for chunk in response:
        if chunk.text:
          yield chunk.text
    except Exception as e:
      yield f"\n[Generation Error: {str(e)}]"

  return StreamingResponse(stream_generator(), media_type="text/plain")
