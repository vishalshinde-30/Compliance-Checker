from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class MongoDB:
    def __init__(self):
        self.client = None
        self.db = None
        self.connect()
    
    def connect(self):
        try:
            # Get the URL from .env
            mongodb_uri = os.getenv("MONGODB_URI")
            
            if not mongodb_uri:
                print("⚠️ No MONGODB_URI found, using local MongoDB")
                mongodb_uri = "mongodb://localhost:27017/"
            
            # Connect with timeout
            self.client = MongoClient(
                mongodb_uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000
            )
            
            # Test connection
            self.client.admin.command('ping')
            
            # Get database name from URI or use default
            if "mongodb+srv://" in mongodb_uri:
                # Extract db name from URI or use default
                if "/compliance_checker" in mongodb_uri:
                    self.db = self.client["compliance_checker"]
                else:
                    self.db = self.client.get_database()
            else:
                self.db = self.client["compliance_checker"]
            
            print("✅ Connected to MongoDB successfully")
            
        except Exception as e:
            print(f"❌ MongoDB Connection Failed: {e}")
            print("⚠️ Switching to in-memory storage...")
            self.use_fallback = True
            self.memory_storage = []
            return
        
        self.use_fallback = False
    
    def get_collection(self, collection_name):
        if self.use_fallback:
            return None
        return self.db[collection_name]
    
    def insert_document(self, collection_name, document):
        if self.use_fallback:
            doc_id = str(datetime.now().timestamp())
            document["_id"] = doc_id
            self.memory_storage.append(document)
            return doc_id
        
        collection = self.get_collection(collection_name)
        result = collection.insert_one(document)
        return str(result.inserted_id)
    
    def get_document(self, collection_name, document_id):
        if self.use_fallback:
            for doc in self.memory_storage:
                if str(doc.get("_id")) == str(document_id):
                    return doc
            return None
        
        collection = self.get_collection(collection_name)
        from bson.objectid import ObjectId
        try:
            doc = collection.find_one({"_id": ObjectId(document_id)})
        except:
            doc = collection.find_one({"_id": document_id})
        return doc
    
    def get_all_documents(self, collection_name):
        if self.use_fallback:
            return self.memory_storage
        
        collection = self.get_collection(collection_name)
        documents = list(collection.find({}))
        
        # Convert ObjectId to string
        for doc in documents:
            if doc and '_id' in doc:
                doc['_id'] = str(doc['_id'])
        
        return documents

# Singleton instance
mongo_db = MongoDB()