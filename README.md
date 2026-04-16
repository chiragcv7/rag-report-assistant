# RAG Report Assistant 🤖📊

An AI-powered analytics tool that lets users query CSV data in plain English.  
Upload a dataset, ask business questions naturally, and get instant answers powered by dynamic Pandas code generation.

---

## 🚀 Features

- 📂 Upload any CSV dataset
- 💬 Ask questions in plain English  
  _Example: "What is the average revenue by region?"_
- ⚙️ Automatically generates and executes Pandas code
- 🧠 Returns clear, business-friendly explanations
- 🔍 Transparent workflow — view the generated code
- 💡 Smart question suggestions based on dataset schema

---

## 🧱 Tech Stack

| Layer | Technology |
|------|------------|
| LLM | Anthropic Claude (`claude-haiku-4-5`) |
| Backend | Python, Flask |
| Data | Pandas, NumPy |
| Frontend | HTML, CSS, Vanilla JavaScript |

---

## ⚙️ Setup

### 1. Install dependencies
pip install -r requirements.txt

### 2. Set your API key
export ANTHROPIC_API_KEY=your_key_here

### 3. Run backend
python app.py

### 4. Start frontend
python -m http.server 8080

Open in browser:
http://127.0.0.1:8080/index.html

---

## 💡 Example Questions

- What is the total revenue?
- What is the total revenue by region?
- Which product generated the most revenue?
- What is the average price by category?
- Show the top 10 customers by revenue
- Are there any missing values in the dataset?

---

## 🏗️ Architecture

User (Browser)
    │
    ├─ Upload CSV ──────► Flask /upload ──► Pandas DataFrame (in-memory)
    │
    ├─ Ask Question ────► Flask /query
    │                         │
    │                         ├─► Claude → Generate Pandas code
    │                         ├─► Python exec() → Run code
    │                         └─► Claude → Explain result
    │
    └─ Suggestions ─────► Flask /suggest ──► Claude → Analyze schema

---

## ⚠️ Limitations

- Supports CSV files only
- Data stored in memory (no persistence)
- Depends on API credits
- Code execution uses `exec()` and is not sandboxed

---

## 📸 Screenshots

### Query & Answer
![Answer](screenshots/answer.png)

### Generated Code
![Code](screenshots/code.png)

---

## 🧠 How it works

1. User uploads a CSV and it is loaded into Pandas
2. User asks a question in plain English
3. Claude generates Pandas code to answer it
4. Backend executes the code
5. Result is explained in plain English and shown with the generated code

---


## 🎯 Why this project matters

This project demonstrates:

- LLM + backend integration
- Real-world data analytics workflows
- Dynamic code generation and execution
- Building tools for non-technical users
