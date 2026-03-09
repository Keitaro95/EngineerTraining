from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.v1.router import router as v1_router
from api.v2.router import router as v2_router

# 大前提これ大事
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://frontend.example.com"],
    allow_credentials=True, #Cookie, 認証ヘッダーありだよ
    allow_methods=["*"], # post, とか get メソッド
    allow_headers=["*"],
    max_age=600, # プリフライト
)

# appに router入れるよ
app.include_router(v1_router, prefix="/api")
app.include_router(v2_router, prefix="/api")
