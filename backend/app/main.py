
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routes.document import router as document_router


app = FastAPI(
    title="Intelligent Document Extraction API",
    description="AI-powered financial document extraction and validation platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "https://intelligent-document-extraction-frontend.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# API ROUTERS
# =========================================================

app.include_router(document_router)


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/api/v1/health")
def health_check():
    return {
        "status": "healthy",
        "service": "document-intelligence-api",
    }