import chromadb
from sentence_transformers import SentenceTransformer
import numpy as np
import uuid
from typing import List, Dict
import os

class VectorStore:
    def __init__(self, persist_directory="./chroma_db"):
        # Create directory if not exists
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Get or create collection - SIMPLIFIED VERSION
        try:
            self.collection = self.client.get_collection("legal_documents")
            print(f"✅ Loaded existing collection with {self.collection.count()} documents")
        except:
            self.collection = self.client.create_collection(
                name="legal_documents",
                metadata={"description": "Legal documents for compliance checking"}
            )
            print("✅ Created new collection")

        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Embedding model loaded")

    def generate_embeddings(self, texts: List[str]):
        """Generate embeddings for texts - RETURNS LIST!"""
        embeddings = self.embedding_model.encode(texts)
        return embeddings.tolist()  # ✅ MUST CONVERT TO LIST!

    def add_documents(self, documents: List[Dict]):
        """Add documents to vector store"""
        if not documents:
            print("⚠️ No documents to add")
            return []
        
        texts = [doc["text"] for doc in documents]
        print(f"📊 Adding {len(texts)} document chunks...")
        
        # Generate embeddings
        embeddings = self.generate_embeddings(texts)
        
        # Prepare metadata and IDs
        metadatas = []
        ids = []
        
        for i, doc in enumerate(documents):
            metadata = {
                "title": doc.get("title", "Unknown"),
                "cause": doc.get("cause", "General Compliance"),
                "chunk_id": doc.get("chunk_id", f"chunk_{i}"),
                "document_id": doc.get("document_id", ""),
                "chunk_index": i
            }
            metadatas.append(metadata)
            ids.append(f"{doc.get('document_id', 'doc')}_{i}")
        
        # Add to collection
        try:
            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            print(f"✅ Successfully added {len(ids)} chunks to vector store")
            return ids
        except Exception as e:
            print(f"❌ Error adding to vector store: {e}")
            return []

    def similarity_search(self, query: str, threshold: float = 0.7, top_k: int = 5):
        """Search for similar documents"""
        print(f"🔍 Searching for: '{query[:50]}...' (threshold: {threshold})")
        
        try:
            # Count documents first
            total_docs = self.collection.count()
            print(f"📊 Total documents in collection: {total_docs}")
            
            if total_docs == 0:
                print("⚠️ No documents in vector store")
                return []
            
            # Generate query embedding
            query_embedding = self.generate_embeddings([query])
            
            # Perform search
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=min(top_k, total_docs),
                include=["documents", "metadatas", "distances"]
            )
            
            search_results = []
            
            if results["documents"] and len(results["documents"][0]) > 0:
                print(f"📈 Found {len(results['documents'][0])} potential matches")
                
                for i in range(len(results["documents"][0])):
                    distance = results["distances"][0][i]
                    similarity_score = 1 - distance
                    
                    if similarity_score >= threshold:
                        search_results.append({
                            "similarity_score": round(similarity_score, 3),
                            "matching_text": results["documents"][0][i],
                            "cause": results["metadatas"][0][i].get("cause", "Unknown"),
                            "document_title": results["metadatas"][0][i].get("title", "Unknown"),
                            "document_id": results["metadatas"][0][i].get("document_id", "")
                        })
            
            print(f"✅ Returning {len(search_results)} matches above threshold {threshold}")
            return search_results
            
        except Exception as e:
            print(f"❌ Error in similarity search: {e}")
            return []

    def get_collection_info(self):
        """Get information about the collection"""
        try:
            count = self.collection.count()
            return {
                "collection_name": "legal_documents",
                "document_count": count,
                "status": "active"
            }
        except:
            return {"error": "Unable to get collection info"}