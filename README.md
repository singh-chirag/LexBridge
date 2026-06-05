# LexBridge
# https://lexbridge-4.onrender.com
# ⚖️ LexBridge — AI Legal Aid Assistant

LexBridge is an AI-powered legal document analysis system designed to help users understand complex legal notices, contracts, debt collection letters, eviction notices, immigration documents, and other legal paperwork using LLMs, OCR, RAG, and workflow orchestration.

The system combines LangGraph multi-step reasoning, FAISS vector retrieval, OCR-based document parsing, and plain-language legal explanations into a production-style AI pipeline.

---

# 🚀 Features

* 📄 PDF + scanned document parsing
* 🔍 OCR extraction using Tesseract
* 🧠 Legal document classification
* ⚠️ Legal risk extraction and severity analysis
* 🗣️ Plain-language explanations for complex legal clauses
* 📚 RAG-powered legal rights retrieval using FAISS
* 📝 Draft legal response generation
* 🌐 Multi-language support
* ⚡ LangGraph multi-node workflow orchestration
* 🖥️ Interactive Streamlit UI
* 🔗 FastAPI backend API
* 🤖 Multi-provider LLM support (Groq / Gemini)

---

# 🏗️ System Architecture

```text
User Upload
     ↓
OCR / PDF Parsing
     ↓
Document Classification
     ↓
Risk Extraction
     ↓
Plain-Language Explanation
     ↓
RAG Legal Rights Retrieval
     ↓
Action Plan Generation
     ↓
Draft Response Letter
```

---

# 🧠 Tech Stack

## Backend

* FastAPI
* LangGraph
* LangChain
* Python

## AI / NLP

* Groq / Gemini APIs
* Sentence Transformers
* FAISS Vector Search
* RAG Pipeline

## OCR / Parsing

* PyMuPDF
* Tesseract OCR
* Pillow

## Frontend

* Streamlit

---

# 📂 Project Structure

```text
LexBridge/
│
├── agent/
│   ├── graph.py
│   └── __init__.py
│
├── app/
│   ├── main.py
│   └── __init__.py
│
├── parsers/
│   ├── pdf_parser.py
│   ├── ocr_parser.py
│   └── doc_classifier.py
│
├── rag/
│   ├── build_kb.py
│   ├── retriever.py
│   ├── legal_kb.faiss
│   └── sources/
│
├── ui/
│   └── streamlit_app.py
│
├── sample_docs/
├── requirements.txt
├── Dockerfile
└── README.md
```

---

# ⚙️ Installation

## 1️⃣ Clone Repository

```bash
git clone https://github.com/singh-chirag/LexBridge.git
cd LexBridge
```

---

## 2️⃣ Create Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / Mac

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🔐 Environment Variables

Create `.env`

```env
LLM_PROVIDER=groq

GROQ_API_KEY=your_api_key

MODEL_NAME=llama-3.3-70b-versatile

TEMPERATURE=0.1
```

---

# 🧠 Build RAG Knowledge Base

```bash
python rag/build_kb.py
```

Expected:

```text
✅ Knowledge base built successfully!
```

---

# 🚀 Run Backend API

```bash
uvicorn app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

Docs:

```text
http://127.0.0.1:8000/docs
```

---

# 🖥️ Run Streamlit UI

```bash
streamlit run ui/streamlit_app.py
```

---

# 📄 Supported Documents

* Eviction notices
* Rental agreements
* Debt collection notices
* Employment contracts
* Immigration notices
* Legal summons
* Consumer legal forms

---

# ⚠️ Disclaimer

LexBridge is an educational AI legal assistance project.

It does NOT replace licensed legal professionals and should not be treated as formal legal advice.

Users should consult qualified attorneys for real legal matters.

---

# 🔥 Engineering Highlights

## Multi-Step AI Workflow

Implemented a LangGraph pipeline with modular AI reasoning nodes:

* Parsing
* Classification
* Risk analysis
* Legal rights retrieval
* Response drafting

---

## Retrieval-Augmented Generation (RAG)

Built a FAISS-based legal retrieval system using sentence-transformer embeddings for grounding responses in legal knowledge.

---

## OCR + PDF Hybrid Extraction

Designed a smart parsing pipeline that:

* extracts text directly from PDFs
* falls back to OCR for scanned/image-based documents

---

## Provider Abstraction

Supports multiple LLM providers including:

* Groq
* Gemini

allowing flexible deployment and cost optimization.

---

# 📸 Demo

Add screenshots or demo GIFs here.

Example:

```text
assets/demo.gif
```

---

# 🛣️ Future Improvements

* PDF report export
* Citation-based legal grounding
* Confidence scoring
* Multi-agent orchestration
* Cloud deployment
* Real-time case tracking
* Voice-based legal assistance
* Legal memory + history

---

# 🤝 Contributing

Pull requests and improvements are welcome.

---

# 📜 License

MIT License

---

# 👨‍💻 Author

Chirag Singh
