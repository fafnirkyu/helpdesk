# 🤖 AI-Powered Helpdesk Automation System

### Developed by [Antonio Carlos Borges Neto](https://github.com/fafnirkyu)

---

## 📋 Overview

This project is a **production-ready AI Helpdesk Automation System** deployed on **Amazon AWS**. It demonstrates a sophisticated full-stack integration designed to automate customer support workflows using local LLMs. 

The system analyzes tickets, performs RAG-based knowledge retrieval, generates context-aware responses, and manages the entire lifecycle via a professional analytics dashboard.

---

## ⚙️ Architecture & Cloud Deployment

The system is hosted on an **AWS EC2 (Ubuntu)** instance, utilizing a production-grade process management layer.



### ☁️ DevOps & Optimization Highlights

Deploying AI to a memory-constrained **AWS t3.micro (1GB RAM)** required significant engineering:

* **Memory-Optimized RAG:** Loading 26,000+ vector entries normally exceeds 1GB RAM. I optimized this by using **NumPy Memory Mapping (`mmap_mode`)**, allowing the system to query the vector store directly from disk. This reduced startup time from **30 minutes to 5 seconds**.
* **Process Management:** Utilized **PM2** to manage the FastAPI and Streamlit services, ensuring 24/7 uptime, auto-restart on failure, and log rotation.
* **Production Networking:** Configured a custom Ubuntu environment to serve the API on privileged **Port 80** and secured the instance via **AWS Security Groups**.

---

## 🚀 Key Features

### 🧠 AI Ticket Classification & RAG

- **Core Engine:** Local inference using `llama3.2:3b` via Ollama for privacy and cost-efficiency.
- **RAG Implementation:** Pulls top-k relevant historical instructions from a pre-calculated vector store to ground LLM responses in company truth.
- **JSON Recovery:** Implementing regex-based recovery to ensure 100% valid JSON output even if the LLM adds conversational filler.

### 💬 Zendesk Integration

- **Auto-Processor:** A background service that polls the Zendesk REST API for new tickets and posts AI-generated responses.
- **Realistic Simulation:** Includes a custom **Seeder** script to populate Zendesk with diverse test cases (billing, tech support, etc.) for demonstration.

### 📊 Streamlit Dashboard

- **Real-time Analytics:** Track category distribution, sentiment trends, and AI confidence levels.
- **Filtering & Sorting:** Interactive UI to drill down into specific ticket types and audit AI responses.

---

## 🧠 Technical Highlights

1. **Forced JSON Extraction:** Early iterations produced inconsistent outputs. I solved this by implementing structured validation and regex-based recovery, resulting in **100% valid JSON output** across all test cases.
2. **Model Optimization:** Iteratively tested multiple models (`mistral:7b`, `llama3.1:8b`) before selecting **`llama3.2:3b`** as the perfect balance between accuracy and 1-2 second latency on micro-instances.
3. **Robust Error Handling:** The system gracefully handles malformed API responses, connection timeouts, and database rollbacks during failed commits.

---

## 🧱 Challenges & Lessons Learned

| Challenge | Engineering Solution |
| :--- | :--- |
| **AWS Resource Constraints** | Optimized RAG to use pre-calculated `.npz` vector archives with disk-mapping. |
| **Inconsistent LLM Output** | Implemented regex extraction and structured fallback logic. |
| **Circular Imports** | Refactored the AI pipeline to use lazy-loading for heavy model components. |
| **Realistic Simulation** | Built a Zendesk seeder to generate synthetic tickets for production testing. |

---

## 🧪 Results

- ✅ **100% Accuracy** across benchmark dataset for classification.
- ⚡ **1-2 Second Latency** per ticket inference.
- 💾 **Automated Sync** with local SQLite DB for historical auditing.
- 💬 **Automatic Posting** confirmed live in Zendesk UI.

---

## 🧰 Tech Stack

- **Cloud:** Amazon AWS (EC2), PM2, Ubuntu Linux
- **AI/ML:** Ollama (Llama 3.2), Sentence-Transformers, NumPy (Vector Search)
- **Backend:** FastAPI, SQLAlchemy, Uvicorn, SQLite
- **Frontend:** Streamlit, Plotly
- **API:** Zendesk REST API

---

## 🛠️ Installation & Production Setup

1. **Clone & Install**
   ```bash
   git clone [https://github.com/fafnirkyu/helpdesk-ai.git](https://github.com/fafnirkyu/helpdesk-ai.git)
   cd helpdesk-ai
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Run via PM2 (Production)**
  ```bash
  # Start the API on Port 80
sudo pm2 start "venv/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 80" --name helpdesk-api

# Start the Dashboard on Port 8501
sudo pm2 start "venv/bin/python3 -m streamlit run dashboard.py --server.port 8501" --name helpdesk-dashboard
  ```

Author: Antonio Carlos Borges Neto

Email: borgesneto.ag_@hotmail.com