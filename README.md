# Compliance Checker System 🔐

## Introduction

The Compliance Checker System is a tool that helps you check if legal documents follow rules and regulations. It works by comparing clauses and sections from your documents using **semantic similarity**. This means it understands the meaning of text, not just the exact words, making it smart enough to find compliance issues even when the wording is different.

---

## Features ✨

- 📄 **Upload PDF Documents** - Easily upload legal documents and policies
- 🔍 **Smart Comparison** - Uses AI to compare document clauses for compliance
- 🏷️ **Organize by Type** - Sort documents as contracts, policies, regulations, or case law
- ⚡ **Fast Search** - Quickly find relevant clauses and regulations
- 🌐 **Web Interface** - Simple, easy-to-use dashboard to manage documents
- 📊 **Clear Results** - Get detailed reports showing compliance issues
- ✅ **Reliable** - Fully tested and ready for production use

---

## Tech Stack 🛠️

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **API** | FastAPI | Web server for handling requests |
| **Frontend** | Streamlit | User-friendly web dashboard |
| **Embeddings** | Sentence-Transformers | Converts text to meaningful vectors |
| **Vector Database** | ChromaDB | Stores and searches document embeddings |
| **PDF Processing** | PyPDF | Reads and extracts text from PDFs |
| **Validation** | Pydantic | Ensures data is correct before processing |
| **Testing** | Pytest | Runs automated tests to check quality |

---

## How It Works 🧠

1. **Upload Documents** - You upload a legal document (PDF format)
2. **Process Text** - The system extracts text and breaks it into chunks
3. **Create Embeddings** - Each chunk is converted to a mathematical representation
4. **Store in Database** - These representations are saved in ChromaDB for fast searching
5. **Compare Clauses** - When you check compliance, the system compares your text against all stored documents
6. **Find Matches** - It finds similar clauses and shows how closely they match
7. **Report Results** - You get a clear report of what complies and what doesn't

---

## Usage Steps 📖

### Step 1: Setup

```bash
# Install Python dependencies
pip install -r requirements.txt
```

### Step 2: Start the API Server

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will run at `http://localhost:8000`

### Step 3: Start the Dashboard

In a new terminal:

```bash
streamlit run frontend/app.py
```

The dashboard will open at `http://localhost:8501`

### Step 4: Upload a Document

1. Open the dashboard
2. Click "Upload Document"
3. Enter document title and category
4. Upload a PDF file
5. Click "Upload" and wait for processing

### Step 5: Check Compliance

1. Go to the "Check Compliance" section
2. Paste or type the text you want to check
3. Click "Check Compliance"
4. View results showing:
   - Compliance score
   - Matching regulations
   - Similarity percentage

---

## Example: Simple Workflow

```
User uploads GDPR Policy (PDF)
         ↓
System extracts text and creates embeddings
         ↓
User enters: "We collect user data for marketing"
         ↓
System finds similar clauses in GDPR
         ↓
Results show: 92% match with "Data Usage Restrictions"
         ↓
User knows there's a compliance issue to review
```

---

## File Structure 📁

```
Compliance-Checker/
├── backend/              # API code
│   ├── main.py          # Main API endpoints
│   ├── models.py        # Data structures
│   ├── database.py      # Database operations
│   └── similarity_search.py  # Compliance checking logic
├── frontend/            # Dashboard code
│   └── app.py          # Streamlit interface
├── tests/              # Test files
└── requirements.txt    # Python packages needed
```

---

## Conclusion 🎯

The Compliance Checker System makes it easy to ensure your documents follow legal requirements. By using smart AI technology to understand document meaning, it helps you find compliance issues quickly and accurately. Whether you're checking contracts, policies, or new regulations, this system gives you confidence that your documents are compliant.

**Get started now**: Upload your first document and check compliance in just a few clicks!

---

## Quick Help 💡

**Problem**: ModuleNotFoundError
- **Fix**: Run `pip install -r requirements.txt`

**Problem**: Port 8000 already in use
- **Fix**: Run `uvicorn main:app --port 8001`

**Problem**: PDF upload fails
- **Fix**: Make sure the file is a valid PDF and not corrupted
