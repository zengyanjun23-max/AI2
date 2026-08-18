import base64
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from google import genai
from google.genai import types
from pydantic import BaseModel

app = FastAPI()

# 跨域資源共享設定，確保前端可存取 API
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

    # 處理前端傳來的 Base64 圖片
    if request.image:
        try:
            image_bytes = base64.b64decode(request.image)
            contents.append(
                types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
            )
        except Exception as e:
            print(f"Image decode error: {e}")

    # 組合 Prompt 提示詞
    prompt = (
        f"Please reply in {request.language}. {request.message}"
        if request.message
        else f"Please describe this image in {request.language}."
    )
    contents.append(prompt)

    # 以串流（Streaming）方式輸出 AI 回應內容
    def stream_generator():
        try:
            # 優先使用額度較寬裕且穩定的 1.5-flash 模型，避免頻繁觸發額度限制
            response = client.models.generate_content_stream(
                model="gemini-3.5-flash", contents=contents
            )
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            error_str = str(e)
            # 擷取 429 或配額用盡錯誤，轉換為優雅的提示文字
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                yield "\n[今天額度用光了，明天才會刷回滿血 🔋]"
            else:
                yield f"\n[連線異常: {error_str}]"

    return StreamingResponse(stream_generator(), media_type="text/plain")
