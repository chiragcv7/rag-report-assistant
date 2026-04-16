# RAG Report Assistant 🤖📊

Query any CSV file in plain English using Claude AI. Upload your data, ask questions naturally, and get instant answers with the generated Python code shown transparently.

## What it does

- Upload any CSV file
- Ask questions in plain English: *"What's the average revenue by region?"*
- Claude generates Pandas code, runs it, and explains the result clearly
- Auto-suggests smart questions based on your dataset
- Shows the generated code so you can learn from it

## Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM | Anthropic Claude (claude-sonnet-4) |
| Backend | Python / Flask |
| Data | Pandas + NumPy |
| Frontend | HTML / CSS / Vanilla JS |

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set your Anthropic API key
```bash
export ANTHROPIC_API_KEY=your_key_here
```

### 3. Run the backend
```bash
python app.py
```

### 4. Open the UI
Open `index.html` in your browser (or serve it with `python -m http.server 8080`).

## Example Questions

- "What is the total sales by category?"
- "Which product has the highest average price?"
- "Are there any missing values in the dataset?"
- "Show me the top 10 customers by revenue"
- "What is the month-over-month growth trend?"

## Architecture

```
User (Browser)
    │
    ├─ Upload CSV ──────► Flask /upload ──► Pandas DataFrame (in-memory)
    │
    ├─ Ask Question ────► Flask /query
    │                         │
    │                         ├─► Claude: Generate Pandas code
    │                         ├─► Python exec() runs the code
    │                         └─► Claude: Explain result in English
    │
    └─ Get Suggestions ─► Flask /suggest ──► Claude: Analyse schema
```

## Resume Bullet Points (copy these!)

> Built an AI-powered RAG report assistant using Python, Flask, and the Anthropic Claude API that lets users query CSV datasets in plain English; Claude dynamically generates and executes Pandas code, then summarises results in business language.

> Designed an LLM-in-the-loop analytics pipeline where natural language questions are translated to executable Python code by Claude, enabling non-technical stakeholders to self-serve data insights without SQL or Pandas knowledge.

## Screenshots

### Query & Answer
![Answer](screenshots/answer.png)
