import os
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List, Dict
import hashlib

class PDFProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        print("✅ PDF Processor initialized")
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract all text from a PDF file"""
        try:
            print(f"📖 Reading PDF: {pdf_path}")
            reader = PdfReader(pdf_path)
            text = ""
            
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            print(f"📄 Extracted {len(text)} characters from PDF")
            return text.strip()
            
        except Exception as e:
            print(f"❌ Error reading PDF {pdf_path}: {e}")
            return ""
    
    def split_document(self, text: str) -> List[Dict]:
        """Split document into chunks with metadata"""
        if not text:
            return []
        
        chunks = self.text_splitter.split_text(text)
        print(f"✂️ Split text into {len(chunks)} chunks")
        
        processed_chunks = []
        for i, chunk in enumerate(chunks):
            # Generate unique ID for each chunk
            chunk_id = hashlib.md5(chunk.encode()).hexdigest()[:10]
            
            # Identify potential cause
            cause = self.identify_cause(chunk)
            
            processed_chunks.append({
                "chunk_id": chunk_id,
                "text": chunk,
                "chunk_index": i,
                "cause": cause,
                "char_length": len(chunk)
            })
        
        return processed_chunks
    
    def identify_cause(self, text: str) -> str:
        """Identify legal cause from text"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["breach", "violation", "non-compliance", "non compliance"]):
            return "Contract Breach"
        elif any(word in text_lower for word in ["privacy", "gdpr", "data protection", "personal data"]):
            return "Privacy Violation"
        elif any(word in text_lower for word in ["intellectual property", "copyright", "patent", "trademark"]):
            return "IP Infringement"
        elif any(word in text_lower for word in ["fraud", "misrepresentation", "deceptive"]):
            return "Fraud"
        elif any(word in text_lower for word in ["liability", "damages", "indemnity", "warranty"]):
            return "Liability Issues"
        elif any(word in text_lower for word in ["payment", "fee", "price", "invoice"]):
            return "Payment Terms"
        elif any(word in text_lower for word in ["confidential", "nda", "non-disclosure", "secret"]):
            return "Confidentiality"
        else:
            return "General Compliance"
    
    def process_pdf(self, pdf_path: str, metadata: Dict = None) -> List[Dict]:
        """Full processing pipeline for a PDF"""
        if metadata is None:
            metadata = {}
        
        # Extract text
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            print("❌ No text extracted from PDF")
            return []
        
        # Split into chunks
        chunks = self.split_document(text)
        
        # Add metadata to each chunk
        for chunk in chunks:
            chunk.update(metadata)
        
        return chunks