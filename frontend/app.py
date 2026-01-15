import streamlit as st
import requests
import os
from datetime import datetime
import io
import PyPDF2

# Backend API URL
API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Compliance Checker",
    page_icon="⚖️",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        color: #1E3A8A;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #1E3A8A 0%, #3B82F6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        margin-bottom: 2rem;
    }
    .stButton > button {
        background-color: #1E3A8A;
        color: white;
        font-weight: bold;
        border-radius: 5px;
    }
    .stButton > button:hover {
        background-color: #3B82F6;
        color: white;
    }
    .upload-box {
        border: 2px dashed #3B82F6;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        margin: 10px 0;
        background-color: #f8f9fa;
    }
    .success-box {
        background-color: #D1FAE5;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #10B981;
        margin: 10px 0;
    }
    .warning-box {
        background-color: #FEF3C7;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #F59E0B;
        margin: 10px 0;
    }
    .error-box {
        background-color: #FEE2E2;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #EF4444;
        margin: 10px 0;
    }
    .delete-btn {
        background-color: #EF4444 !important;
        color: white !important;
    }
    .delete-btn:hover {
        background-color: #DC2626 !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []
if 'selected_doc' not in st.session_state:
    st.session_state.selected_doc = None
if 'compliance_results' not in st.session_state:
    st.session_state.compliance_results = None
if 'show_delete_confirm' not in st.session_state:
    st.session_state.show_delete_confirm = None

# App Header
st.markdown("<h1 class='main-header'>⚖️ Legal Compliance Checker</h1>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("📍 Navigation")
    page = st.radio(
        "Go to",
        ["📤 Upload Documents", "🔍 Check Compliance", "📚 View Documents", "📊 Dashboard"],
        label_visibility="collapsed"
    )
    
    st.divider()
    
    st.header("⚙️ Settings")
    similarity_threshold = st.slider(
        "Similarity Threshold",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        help="Higher values require closer matches"
    )
    
    st.divider()
    
    st.header("🔗 API Status")
    
    # Health check
    if st.button("Check API Health", key="health_check"):
        try:
            response = requests.get(f"{API_URL}/health", timeout=5)
            if response.status_code == 200:
                st.success("✅ API Connected")
            else:
                st.error(f"❌ API Error: Status {response.status_code}")
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to API")
            st.info("Start backend: python -m uvicorn backend.main:app --reload")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# ==================== UPLOAD DOCUMENTS PAGE ====================
if page == "📤 Upload Documents":
    st.header("📤 Upload Legal Document")
    
    with st.form("upload_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input(
                "**Document Title***", 
                placeholder="E.g., Service Agreement 2024",
                help="Enter a descriptive title"
            )
        
        with col2:
            category = st.selectbox(
                "**Category***",
                ["Contract", "Policy", "Regulation", "Case Law", "Other"],
                index=0,
                help="Select document category"
            )
        
        description = st.text_area(
            "**Description**", 
            placeholder="Brief description (optional)",
            height=100
        )
        
        st.markdown('<div class="upload-box">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "**Choose PDF file***", 
            type="pdf",
            help="Select a PDF to upload and index"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        if uploaded_file:
            file_size = uploaded_file.size
            st.info(f"📄 **Selected:** {uploaded_file.name} ({file_size/1024:.1f} KB)")
        
        submitted = st.form_submit_button("🚀 Upload & Index Document", type="primary")
        
        if submitted:
            if not title:
                st.error("❌ Please enter a document title")
            elif not uploaded_file:
                st.error("❌ Please select a PDF file")
            else:
                with st.spinner("📤 Uploading and processing..."):
                    try:
                        files = {
                            'file': (uploaded_file.name, uploaded_file.getvalue(), 'application/pdf')
                        }
                        
                        data = {
                            'title': title,
                            'description': description,
                            'category': category.lower().replace(" ", "_")
                        }
                        
                        response = requests.post(
                            f"{API_URL}/upload/",
                            files=files,
                            data=data,
                            timeout=30
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.markdown('<div class="success-box">', unsafe_allow_html=True)
                            st.success("✅ **Document uploaded and indexed!**")
                            st.write(f"**Title:** {result['title']}")
                            st.write(f"**ID:** {result['id']}")
                            st.write(f"**Category:** {result['category'].replace('_', ' ').title()}")
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            with st.expander("📋 View Details", expanded=False):
                                st.json(result)
                            
                            st.session_state.uploaded_files.append({
                                "id": result["id"],
                                "title": result["title"],
                                "uploaded_at": result["uploaded_at"]
                            })
                            
                        else:
                            st.markdown('<div class="error-box">', unsafe_allow_html=True)
                            try:
                                error_detail = response.json().get('detail', 'Unknown error')
                                st.error(f"❌ Upload failed: {error_detail}")
                            except:
                                st.error(f"❌ Upload failed with status: {response.status_code}")
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                    except requests.exceptions.ConnectionError:
                        st.error("❌ Cannot connect to backend server")
                        st.info("Run: `python -m uvicorn backend.main:app --reload`")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

# ==================== CHECK COMPLIANCE PAGE ====================
elif page == "🔍 Check Compliance":
    st.header("🔍 Check Compliance")
    
        # Input method
    input_method = st.radio(
        "Input Method",
        ["✍️ Text Input", "📄 Upload Document"],
        horizontal=True,
        label_visibility="collapsed"
    )

    query_text = ""

    if input_method == "✍️ Text Input":
        st.markdown("**Enter text to check for compliance:**")
        
        query_text = st.text_area(
            "Paste text here:",
            height=200,
            placeholder="""Paste contract clause, policy text, or legal query here...

Example: Employee cannot work in same industry for 10 years after leaving job.""",
            key="query_text_area"
        )
        
    else:
        uploaded_query = st.file_uploader(
            "Upload document for checking", 
            type="pdf",
            help="Upload a PDF to check"
        )
        
        if uploaded_query:
            try:
                reader = PyPDF2.PdfReader(io.BytesIO(uploaded_query.getvalue()))
                extracted_text = ""
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        extracted_text += text
                
                if extracted_text.strip():
                    st.success(f"✅ Extracted {len(extracted_text)} characters")
                    query_text = st.text_area(
                        "Extracted Text:",
                        value=extracted_text[:2000],
                        height=200,
                        key="extracted_text"
                    )
                else:
                    st.warning("⚠️ No text extracted. Try text input.")
            except Exception as e:
                st.error(f"❌ PDF Error: {str(e)}")
    
    # Advanced options
    with st.expander("⚙️ Advanced Options", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            threshold = st.slider(
                "Similarity Threshold",
                min_value=0.0,
                max_value=1.0,
                value=similarity_threshold,
                help="Minimum similarity to show (0.0 to 1.0)"
            )
        with col2:
            top_k = st.number_input(
                "Max Results",
                min_value=1,
                max_value=20,
                value=5,
                help="Maximum results to return"
            )
    
    # Check Compliance button
    check_button = st.button("🔍 Check Compliance", type="primary", key="check_compliance_main", use_container_width=True)
    
    if check_button:
        if not query_text or not query_text.strip():
            st.warning("⚠️ Please enter some text to check")
        elif len(query_text.strip()) < 5:
            st.warning("⚠️ Please enter at least 5 characters")
        else:
            with st.spinner("🔍 Analyzing for compliance issues..."):
                try:
                    response = requests.post(
                        f"{API_URL}/check-compliance/",
                        json={
                            "query_text": query_text.strip(),
                            "threshold": threshold,
                            "top_k": top_k
                        },
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        report = response.json()
                        st.session_state.compliance_results = report
                        
                        # Display results
                        st.markdown("---")
                        st.markdown("## 📊 Analysis Results")
                        
                        # Get values safely
                        total_matches = report.get("total_matches", 0)
                        high_risk_causes = report.get("high_risk_causes", [])
                        results_by_cause = report.get("results_by_cause", {})
                        recommendations = report.get("recommendations", [])
                        
                        # Metrics
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total Matches", total_matches)
                        with col2:
                            st.metric("High Risk Issues", len(high_risk_causes))
                        with col3:
                            if high_risk_causes:
                                risk = "🔴 HIGH"
                            elif total_matches > 0:
                                risk = "🟡 MEDIUM"
                            else:
                                risk = "🟢 LOW"
                            st.metric("Risk Level", risk)
                        
                        # High risk causes
                        if high_risk_causes:
                            st.markdown('<div class="warning-box">', unsafe_allow_html=True)
                            st.markdown("### 🚨 High Risk Compliance Issues")
                            for risk in high_risk_causes:
                                st.write(f"**{risk.get('cause', 'Unknown')}**: {risk.get('count', 0)} matches")
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Detailed results
                        if results_by_cause:
                            st.markdown("### 📋 Detailed Matches")
                            for cause, docs in results_by_cause.items():
                                with st.expander(f"**{cause}** ({len(docs)} matches)", expanded=False):
                                    for i, doc in enumerate(docs):
                                        st.write(f"**Match {i+1}:** {doc.get('similarity_score', 0):.1%} similar")
                                        st.write(f"**Document:** {doc.get('document_title', 'Unknown')}")
                                        st.text_area(
                                            "Matching Text:",
                                            value=doc.get('matching_text', ''),
                                            height=100,
                                            key=f"match_{cause}_{i}",
                                            disabled=True
                                        )
                                        st.write("---")
                        elif total_matches == 0:
                            st.info("No matches found with current threshold. Try lowering the threshold.")
                        
                        # Recommendations
                        if recommendations:
                            st.markdown("### 💡 Recommendations")
                            for rec in recommendations:
                                st.info(rec)
                        else:
                            if total_matches == 0:
                                st.success("✅ No significant compliance issues found.")
                            else:
                                st.info("Review the matches above for potential issues.")
                    
                    else:
                        st.error(f"❌ API Error: Status {response.status_code}")
                        try:
                            error_detail = response.json().get('detail', response.text[:200])
                            st.error(f"Details: {error_detail}")
                        except:
                            pass
                
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to backend server")
                    st.info("Make sure backend is running: http://localhost:8000")
                except requests.exceptions.Timeout:
                    st.error("❌ Request timed out. Server might be busy.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    # Show previous results if available
    if st.session_state.compliance_results:
        if st.button("🔄 Show Last Results", key="show_last_results"):
            with st.expander("Last Results", expanded=True):
                st.json(st.session_state.compliance_results)

# ==================== VIEW DOCUMENTS PAGE (WITH DELETE) ====================
elif page == "📚 View Documents":
    st.header("📚 Indexed Documents")
    
    try:
        with st.spinner("Loading documents..."):
            response = requests.get(f"{API_URL}/documents/", timeout=10)
            
            if response.status_code == 200:
                documents = response.json()
                
                # Summary
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Documents", len(documents))
                with col2:
                    indexed = len([d for d in documents if d.get("vector_id")])
                    st.metric("Indexed", indexed)
                with col3:
                    if documents:
                        categories = len(set([d.get("category", "").replace("_", " ").title() for d in documents]))
                        st.metric("Categories", categories)
                
                # Search and filter
                st.markdown("### 🔍 Search & Filter")
                search_col1, search_col2 = st.columns([3, 1])
                with search_col1:
                    search_query = st.text_input("Search documents:", placeholder="Search by title or description...", key="doc_search")
                with search_col2:
                    filter_category = st.selectbox("Category", ["All", "Contract", "Policy", "Regulation", "Case Law", "Other"], key="cat_filter")
                
                # Filter documents
                filtered_docs = documents
                if search_query:
                    filtered_docs = [
                        doc for doc in documents 
                        if search_query.lower() in doc.get("title", "").lower() 
                        or search_query.lower() in doc.get("description", "").lower()
                    ]
                
                if filter_category != "All":
                    filtered_docs = [
                        doc for doc in filtered_docs 
                        if doc.get("category", "").replace("_", " ").title() == filter_category
                    ]
                
                # Display documents with DELETE option
                if not filtered_docs:
                    st.info("No documents found matching your criteria.")
                else:
                    st.markdown(f"**Showing {len(filtered_docs)} document(s)**")
                    
                    for doc in filtered_docs:
                        with st.container():
                            st.markdown("---")
                            
                            col1, col2, col3 = st.columns([3, 1, 1])
                            
                            with col1:
                                st.markdown(f"### {doc.get('title', 'Untitled')}")
                                if doc.get("description"):
                                    st.write(f"*{doc.get('description')}*")
                                
                                # Metadata
                                meta_col1, meta_col2, meta_col3 = st.columns(3)
                                with meta_col1:
                                    cat = doc.get("category", "other").replace("_", " ").title()
                                    st.caption(f"**Category:** {cat}")
                                with meta_col2:
                                    date = doc.get("uploaded_at", "")[:10]
                                    st.caption(f"**Uploaded:** {date}")
                                with meta_col3:
                                    if doc.get("vector_id"):
                                        st.success("✅ Indexed")
                                    else:
                                        st.warning("⚠️ Not Indexed")
                            
                            with col2:
                                if st.button("📄 View", key=f"view_{doc.get('id')}"):
                                    st.session_state.selected_doc = doc.get('id')
                                    st.rerun()
                            
                            with col3:
                                # DELETE button with confirmation
                                delete_key = f"delete_{doc.get('id')}"
                                if delete_key not in st.session_state:
                                    st.session_state[delete_key] = False
                                
                                if not st.session_state[delete_key]:
                                    if st.button("🗑️ Delete", key=f"del_btn_{doc.get('id')}"):
                                        st.session_state[delete_key] = True
                                        st.session_state.show_delete_confirm = doc.get('id')
                                        st.rerun()
                                else:
                                    # Show confirmation
                                    st.warning(f"Delete '{doc.get('title', 'this document')}'?")
                                    col_yes, col_no = st.columns(2)
                                    with col_yes:
                                        if st.button("✅ Yes", key=f"confirm_yes_{doc.get('id')}"):
                                            try:
                                                delete_response = requests.delete(f"{API_URL}/document/{doc.get('id')}")
                                                if delete_response.status_code == 200:
                                                    st.success("✅ Document deleted successfully!")
                                                    st.session_state[delete_key] = False
                                                    st.rerun()
                                                else:
                                                    st.error("Failed to delete document")
                                            except:
                                                st.error("Error deleting document")
                                    with col_no:
                                        if st.button("❌ No", key=f"confirm_no_{doc.get('id')}"):
                                            st.session_state[delete_key] = False
                                            st.rerun()
            
            else:
                st.error(f"Failed to fetch documents: Status {response.status_code}")
    
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend server")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

# ==================== DASHBOARD PAGE ====================
elif page == "📊 Dashboard":
    st.header("📊 Dashboard")
    
    try:
        response = requests.get(f"{API_URL}/documents/", timeout=10)
        
        if response.status_code == 200:
            documents = response.json()
            
            if documents:
                # Stats
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total", len(documents))
                with col2:
                    contracts = len([d for d in documents if "contract" in d.get("category", "").lower()])
                    st.metric("Contracts", contracts)
                with col3:
                    policies = len([d for d in documents if "policy" in d.get("category", "").lower()])
                    st.metric("Policies", policies)
                with col4:
                    indexed = len([d for d in documents if d.get("vector_id")])
                    st.metric("Indexed", indexed)
                
                # Categories
                st.subheader("Categories")
                categories = {}
                for doc in documents:
                    cat = doc.get("category", "other").replace("_", " ").title()
                    categories[cat] = categories.get(cat, 0) + 1
                
                # Show categories
                cat_items = list(categories.items())
                for i in range(0, len(cat_items), 3):
                    row = cat_items[i:i+3]
                    cols = st.columns(len(row))
                    for j, (cat, count) in enumerate(row):
                        with cols[j]:
                            st.metric(cat, count)
                
                # Recent uploads
                st.subheader("Recent Uploads")
                recent = sorted(documents, key=lambda x: x.get("uploaded_at", ""), reverse=True)[:5]
                for doc in recent:
                    st.write(f"• **{doc.get('title', 'Untitled')}** - {doc.get('uploaded_at', '')[:10]}")
            
            else:
                st.info("No documents yet. Upload some first!")
        
        else:
            st.error("Failed to fetch data")
    
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

# ==================== FOOTER ====================
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #6B7280;'>
    <strong>Compliance Checker v1.0</strong> | Legal Tech Capstone | Powered by ChromaDB & LangChain
    </div>
    """,
    unsafe_allow_html=True
)