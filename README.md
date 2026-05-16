# ■ LexBridge
> AI legal aid agent. Upload any legal document. Understand it in your language. Know your rights.

[![Hugging Face Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces/YOUR_USERNAME/lexbridge)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)

---

## 🌍 The Problem
- **1 Billion+** people lack access to legal aid globally
- **80%** of low-income legal needs go unmet
- **$300/hr** average lawyer cost vs **$0** for LexBridge

Every day, people receive eviction notices, court summons, predatory contracts, and immigration forms they cannot understand. LexBridge gives everyone the ability to understand any legal document in their own language — and know exactly what to do next.

> This is not a toy. This is infrastructure for human dignity.

---

## ✨ What It Does

1. **Upload** any legal document (PDF or image, any language)
2. **Extract** risks, deadlines, and dangerous clauses using PyMuPDF + Tesseract OCR
3. **Explain** everything in plain language, translated to your detected language
4. **Retrieve** your legal rights via RAG over real government documents (CFPB, HUD, USCIS)
5. **Generate** a prioritized action plan + draft response letter if needed

### Supported Document Types
| Type | Examples | Key Outputs |
|------|----------|-------------|
| 🏠 Eviction Notice | Pay-or-quit notices, lease terminations | Response deadline, tenant rights, cure options |
| 📜 Lease Agreement | Rental contracts, addendums | Unfair clauses, deposit rules, penalty terms |
| ⚖️ Court Summons | Civil/criminal notices | Response deadline, charge type, required forms |
| 💳 Debt Collection | Collection letters, validation notices | FDCPA rights, dispute process, statute of limitations |
| 💼 Employment Contract | Offer letters, non-competes | IP clauses, termination terms, enforceability notes |
| 🛂 Immigration Form | USCIS forms, visa applications | Requirements, deadlines, missing document alerts |

---

## 🏗️ Architecture

### 5-Node LangGraph Pipeline