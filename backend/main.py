from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
from datetime import datetime
from typing import List, Optional

from .models import *
from .database import mongo_db
from .similarity_search import ComplianceChecker

app = FastAPI(title="Compliance Checker API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize compliance checker
checker = ComplianceChecker()

# Ensure upload directory exists
UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

print("🚀 Compliance Checker API Starting...")
print(f"📁 Upload directory: {os.path.abspath(UPLOAD_DIR)}")

@app.get("/")
async def root():
    return {"message": "Compliance Checker API", "status": "running"}

@app.post("/upload/", response_model=DocumentResponse)
async def upload_document(
    title: str = Form(...),
    description: Optional[str] = Form(""),
    category: str = Form("legal"),
    file: UploadFile = File(...)
):
    """Upload and index a PDF document"""
    print(f"📤 Upload request received: {title}")
    print(f"📄 File: {file.filename} ({file.size} bytes)")
    
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Save uploaded file
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1] or '.pdf'
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}{file_extension}")
        
        print(f"💾 Saving file to: {file_path}")
        
        # Read and save file
        contents = await file.read()
        with open(file_path, "wb") as buffer:
            buffer.write(contents)
        
        print(f"✅ File saved successfully ({len(contents)} bytes)")
        
        # Prepare metadata
        document_metadata = {
            "title": title,
            "description": description,
            "category": category,
            "document_id": file_id,
            "file_path": file_path,
            "uploaded_at": datetime.utcnow(),
            "original_filename": file.filename,
            "file_size": len(contents)
        }
        
        # Store in MongoDB
        db_doc = {
            "_id": file_id,
            **document_metadata
        }
        
        print(f"💾 Saving to MongoDB: {title}")
        mongo_db.insert_document("documents", db_doc)
        print("✅ Saved to MongoDB")
        
        # Index document for similarity search
        print(f"🔍 Indexing document with ID: {file_id}")
        index_result = checker.index_document(
            file_path,
            {
                "title": title,
                "description": description,
                "document_id": file_id,
                "category": category,
                "uploaded_at": datetime.utcnow().isoformat()
            }
        )
        
        print(f"📊 Index result: {index_result}")
        
        # Update with vector IDs if indexing was successful
        if index_result["success"]:
            print(f"✅ Indexed {index_result.get('chunks_count', 0)} chunks")
            # Update MongoDB with vector IDs
            mongo_db.get_collection("documents").update_one(
                {"_id": file_id},
                {"$set": {"vector_ids": index_result.get("vector_ids", [])}}
            )
            vector_id = index_result.get("vector_ids", [None])[0]
        else:
            print(f"❌ Indexing failed: {index_result.get('message', 'Unknown error')}")
            vector_id = None
        
        return DocumentResponse(
            id=file_id,
            title=title,
            description=description,
            category=category,
            uploaded_at=document_metadata["uploaded_at"],
            vector_id=vector_id
        )
        
    except Exception as e:
        print(f"❌ Upload error: {str(e)}")
        # Clean up file if error occurred
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/check-compliance/")
async def check_compliance(request: SimilarityRequest):
    """Check compliance for given text"""
    print(f"🎯 Compliance check request: '{request.query_text[:50]}...'")
    print(f"📊 Threshold: {request.threshold}")
    
    try:
        report = checker.check_compliance(
            query_text=request.query_text,
            threshold=request.threshold
        )
        
        print(f"📈 Report generated: {report.get('total_matches', 0)} matches")
        print(f"📊 High risk causes: {len(report.get('high_risk_causes', []))}")
        
        return report
    except Exception as e:
        print(f"❌ Error in compliance check: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents/", response_model=List[DocumentResponse])
async def get_documents():
    """Get all uploaded documents"""
    print("📚 Fetching all documents")
    
    try:
        documents = mongo_db.get_all_documents("documents")
        print(f"📊 Found {len(documents)} documents in MongoDB")
        
        response_docs = []
        for doc in documents:
            # Convert MongoDB ObjectId to string
            doc_id = str(doc["_id"]) if "_id" in doc else str(doc.get("document_id", ""))
            
            response_docs.append(DocumentResponse(
                id=doc_id,
                title=doc.get("title", "Untitled"),
                description=doc.get("description", ""),
                category=doc.get("category", "legal"),
                uploaded_at=doc.get("uploaded_at", datetime.utcnow()),
                vector_id=doc.get("vector_ids", [None])[0] if doc.get("vector_ids") else None
            ))
        
        print(f"✅ Returning {len(response_docs)} documents")
        return response_docs
    except Exception as e:
        print(f"❌ Error fetching documents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch documents: {str(e)}")

@app.get("/document/{document_id}")
async def get_document(document_id: str):
    """Get a specific document by ID"""
    print(f"🔍 Fetching document: {document_id}")
    
    try:
        document = mongo_db.get_document("documents", document_id)
        if not document:
            print(f"❌ Document not found: {document_id}")
            raise HTTPException(status_code=404, detail="Document not found")
        
        print(f"✅ Found document: {document.get('title', 'Untitled')}")
        
        return {
            "id": str(document["_id"]),
            "title": document.get("title", "Untitled"),
            "description": document.get("description", ""),
            "category": document.get("category", "legal"),
            "uploaded_at": document.get("uploaded_at"),
            "file_path": document.get("file_path", ""),
            "original_filename": document.get("original_filename", ""),
            "vector_ids": document.get("vector_ids", [])
        }
    except Exception as e:
        print(f"❌ Error fetching document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/document/{document_id}")
async def delete_document(document_id: str):
    """Delete a document by ID"""
    print(f"🗑️ Deleting document: {document_id}")
    
    try:
        # Get document details first
        document = mongo_db.get_document("documents", document_id)
        if not document:
            print(f"❌ Document not found for deletion: {document_id}")
            raise HTTPException(status_code=404, detail="Document not found")
        
        print(f"📄 Document to delete: {document.get('title', 'Unknown')}")
        
        # Delete file from filesystem
        file_path = document.get("file_path")
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            print(f"✅ Deleted file: {file_path}")
        else:
            print(f"⚠️ File not found: {file_path}")
        
        # Delete from MongoDB
        collection = mongo_db.get_collection("documents")
        collection.delete_one({"_id": document_id})
        print(f"✅ Deleted from MongoDB")
        
        # Note: Vector store deletion would need separate implementation
        
        return {"message": "Document deleted successfully", "document_id": document_id}
    except Exception as e:
        print(f"❌ Error deleting document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    mongo_status = mongo_db.client is not None
    print(f"🏥 Health check - MongoDB: {'✅ Connected' if mongo_status else '❌ Not connected'}")
    
    return {
        "status": "healthy", 
        "timestamp": datetime.utcnow().isoformat(),
        "mongo_connected": mongo_status,
        "service": "Compliance Checker API",
        "version": "1.0.0"
    }

@app.get("/debug/vector-store")
async def debug_vector_store():
    """Debug endpoint to check vector store status"""
    try:
        # Import here to avoid circular imports
        from .vector_store import VectorStore
        
        vector_store = VectorStore()
        info = vector_store.get_collection_info()
        
        return {
            "status": "success",
            "vector_store": info,
            "message": "Vector store status"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to get vector store info"
        }

@app.get("/debug/check-simple")
async def debug_check_simple():
    """Simple debug endpoint to test similarity search"""
    try:
        # Test with a simple query
        test_query = "payment within 30 days"
        test_threshold = 0.5
        
        report = checker.check_compliance(
            query_text=test_query,
            threshold=test_threshold
        )
        
        return {
            "status": "success",
            "test_query": test_query,
            "test_threshold": test_threshold,
            "result": report
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "test_query": "payment within 30 days"
        }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Compliance Checker API...")
    uvicorn.run(app, host="0.0.0.0", port=8000)