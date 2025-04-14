from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from data_ingestion import DocumentProcessor
from document_analysis import DocumentAnalyzer
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Bank RAG Application")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize processors
document_processor = DocumentProcessor()
document_analyzer = DocumentAnalyzer()

class Query(BaseModel):
    text: str
    k: Optional[int] = 5

class DocumentResponse(BaseModel):
    content: str
    metadata: dict
    similarity_score: Optional[float]

class AnalysisResponse(BaseModel):
    summary: str
    recommendations: List[str]
    sources: List[str]
    token_usage: dict

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a single document"""
    try:
        # Save the uploaded file
        file_path = f"../data/{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process the document
        documents = document_processor.load_document(file_path)
        chunks = document_processor.text_splitter.split_documents(documents)
        
        # Store in vector database
        document_processor.vector_store.add_documents(chunks)
        
        return {"message": f"Successfully processed {file.filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
async def query_documents(query: Query):
    """Query the document store and get analysis"""
    try:
        # Get similar documents
        similar_docs = document_processor.get_similar_documents(query.text, query.k)
        
        # Generate summary with token counts
        summary, summary_tokens = document_analyzer.generate_summary(similar_docs)
        
        # Get recommendations with token counts
        recommendations, rec_tokens = document_analyzer.get_recommendations(similar_docs, query.text)
        
        # Combine token counts
        total_tokens = {
            "summary": summary_tokens,
            "recommendations": rec_tokens,
            "total": {
                "input_tokens": summary_tokens["input_tokens"] + rec_tokens["input_tokens"],
                "output_tokens": summary_tokens["output_tokens"] + rec_tokens["output_tokens"],
                "total_tokens": summary_tokens["total_tokens"] + rec_tokens["total_tokens"]
            }
        }
        
        return AnalysisResponse(
            summary=summary,
            recommendations=[recommendations["recommendations"]],
            sources=recommendations["sources"],
            token_usage=total_tokens
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat-history")
async def get_chat_history():
    """Get the conversation history"""
    try:
        return document_analyzer.get_chat_history()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 