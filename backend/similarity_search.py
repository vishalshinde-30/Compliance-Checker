from typing import List, Dict
from .vector_store import VectorStore
from .document_processor import PDFProcessor

class ComplianceChecker:
    def __init__(self):
        self.vector_store = VectorStore()
        self.pdf_processor = PDFProcessor()
        print("✅ Compliance Checker initialized")
    
    def index_document(self, pdf_path: str, metadata: Dict) -> Dict:
        """Index a new document for similarity search"""
        print(f"📄 Indexing document: {pdf_path}")
        
        # Process PDF
        chunks = self.pdf_processor.process_pdf(pdf_path, metadata)
        
        if not chunks:
            print("❌ Failed to process PDF or no text extracted")
            return {"success": False, "message": "Failed to process PDF"}
        
        print(f"📊 Extracted {len(chunks)} text chunks")
        
        # Add to vector store
        vector_ids = self.vector_store.add_documents(chunks)
        
        if vector_ids:
            print(f"✅ Successfully indexed document with {len(vector_ids)} chunks")
            return {
                "success": True,
                "message": f"Indexed {len(chunks)} chunks",
                "chunks_count": len(chunks),
                "vector_ids": vector_ids,
                "document_id": metadata.get("document_id")
            }
        else:
            print("❌ Failed to add documents to vector store")
            return {"success": False, "message": "Failed to index document"}
    
    def check_compliance(self, query_text: str, threshold: float = 0.7) -> Dict:
        """Check compliance by finding similar cases"""
        print(f"🔍 Checking compliance for query: '{query_text[:100]}...'")
        
        # Search for similar documents
        similar_docs = self.vector_store.similarity_search(
            query_text, 
            threshold=threshold
        )
        
        # Group by cause
        results_by_cause = {}
        for doc in similar_docs:
            cause = doc["cause"]
            if cause not in results_by_cause:
                results_by_cause[cause] = []
            results_by_cause[cause].append(doc)
        
        # Identify high-risk causes (multiple similar cases)
        high_risk_causes = []
        for cause, docs in results_by_cause.items():
            if len(docs) >= 2:  # If multiple similar cases found
                avg_similarity = sum(d["similarity_score"] for d in docs) / len(docs)
                high_risk_causes.append({
                    "cause": cause,
                    "count": len(docs),
                    "avg_similarity": round(avg_similarity, 3)
                })
        
        # Generate recommendations
        recommendations = []
        if high_risk_causes:
            recommendations.append(
                f"⚠️ High similarity found with {len(high_risk_causes)} compliance issues. Review carefully."
            )
        elif similar_docs:
            recommendations.append(
                "ℹ️ Some similarities found. Consider reviewing these areas."
            )
        else:
            recommendations.append(
                "✅ No significant similarity found with known compliance issues."
            )
        
        # Prepare final report
        compliance_report = {
            "query": query_text,
            "threshold": threshold,
            "total_matches": len(similar_docs),
            "results_by_cause": results_by_cause,
            "high_risk_causes": high_risk_causes,
            "recommendations": recommendations
        }
        
        print(f"📊 Compliance check complete: {len(similar_docs)} matches found")
        return compliance_report