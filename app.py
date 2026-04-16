"""
RAG Report Assistant - Backend
Lets users upload a CSV and query it in plain English using Claude.
"""

import os
import json
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
import anthropic

app = Flask(__name__)
CORS(app)

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# In-memory store for uploaded dataframes (keyed by session id)
dataframes = {}


def df_to_context(df: pd.DataFrame, max_rows: int = 50) -> str:
    """Convert a dataframe to a string context for the LLM."""
    shape = df.shape
    dtypes = df.dtypes.to_dict()
    dtype_str = ", ".join(f"{col}: {dtype}" for col, dtype in dtypes.items())
    
    # Summary stats
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    stats = ""
    if numeric_cols:
        stats = "\n\nNumerical Summary:\n" + df[numeric_cols].describe().to_string()
    
    # Sample rows
    sample = df.head(max_rows).to_string(index=False)
    
    return f"""Dataset Shape: {shape[0]} rows x {shape[1]} columns
Columns and Types: {dtype_str}
{stats}

Sample Data (first {min(max_rows, shape[0])} rows):
{sample}"""


def run_analysis(df: pd.DataFrame, question: str) -> dict:
    """
    Use Claude to:
    1. Generate Python/pandas code to answer the question
    2. Execute it
    3. Summarise the result in plain English
    """
    context = df_to_context(df)
    
    # Step 1: Ask Claude to write analysis code
    code_prompt = f"""You are a data analyst. A user has uploaded a CSV dataset and asked a question.
Your job is to write Python/pandas code to answer their question.

Dataset info:
{context}

User question: {question}

Write Python code using a variable called `df` (already loaded as a pandas DataFrame).
Store your final answer in a variable called `result`.
result should be a string, number, DataFrame, or list — whatever best answers the question.
Return ONLY the Python code, no markdown fences, no explanation."""

    code_response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1000,
        messages=[{"role": "user", "content": code_prompt}]
    )
    
    code = code_response.content[0].text.strip()
    # Strip markdown fences if model adds them
    if code.startswith("```"):
        code = "\n".join(code.split("\n")[1:])
    if code.endswith("```"):
        code = "\n".join(code.split("\n")[:-1])
    
    # Step 2: Execute the code safely
    local_vars = {"df": df.copy(), "pd": pd, "np": np}
    try:
        exec(code, {}, local_vars)
        result = local_vars.get("result", "No result variable found.")
        
        # Convert result to string for LLM
        if isinstance(result, pd.DataFrame):
            result_str = result.to_string(index=False)
        elif isinstance(result, (list, dict)):
            result_str = json.dumps(result, default=str, indent=2)
        else:
            result_str = str(result)
        
        error = None
    except Exception as e:
        result_str = None
        error = str(e)
    
    # Step 3: Ask Claude to explain the result
    if error:
        explain_prompt = f"""A user asked: "{question}"

The code failed with error: {error}

Please apologise briefly, explain what went wrong in simple terms, and suggest how to rephrase the question.
Keep it under 3 sentences."""
        answer_text = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=500,
            messages=[{"role": "user", "content": explain_prompt}]
        ).content[0].text
        return {"answer": answer_text, "code": code, "raw_result": None, "error": error}
    
    explain_prompt = f"""A user asked: "{question}"

The analysis returned this result:
{result_str}

Write a clear, concise answer in plain English (2-4 sentences). 
Include specific numbers/values from the result.
Be direct — no fluff."""

    answer_response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=500,
        messages=[{"role": "user", "content": explain_prompt}]
    )
    
    answer_text = answer_response.content[0].text
    
    return {
        "answer": answer_text,
        "code": code,
        "raw_result": result_str[:2000] if result_str else None,  # cap size
        "error": None
    }


@app.route("/upload", methods=["POST"])
def upload():
    """Accept a CSV upload and return a session_id + preview."""
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files["file"]
    if not file.filename.endswith(".csv"):
        return jsonify({"error": "Only CSV files are supported"}), 400
    
    try:
        df = pd.read_csv(file)
    except Exception as e:
        return jsonify({"error": f"Could not parse CSV: {str(e)}"}), 400
    
    session_id = str(abs(hash(file.filename + str(df.shape))))
    dataframes[session_id] = df
    
    return jsonify({
        "session_id": session_id,
        "rows": df.shape[0],
        "columns": df.shape[1],
        "column_names": df.columns.tolist(),
        "preview": df.head(5).to_dict(orient="records")
    })


@app.route("/query", methods=["POST"])
def query():
    """Answer a natural language question about the uploaded CSV."""
    body = request.json
    session_id = body.get("session_id")
    question = body.get("question", "").strip()
    
    if not session_id or session_id not in dataframes:
        return jsonify({"error": "Session not found. Please upload a CSV first."}), 400
    if not question:
        return jsonify({"error": "No question provided."}), 400
    
    df = dataframes[session_id]
    result = run_analysis(df, question)
    return jsonify(result)


@app.route("/suggest", methods=["POST"])
def suggest():
    """Return suggested questions based on the dataset."""
    body = request.json
    session_id = body.get("session_id")
    
    if not session_id or session_id not in dataframes:
        return jsonify({"error": "Session not found."}), 400
    
    df = dataframes[session_id]
    context = df_to_context(df, max_rows=10)
    
    prompt = f"""Given this dataset:
{context}

Suggest 5 insightful questions a business analyst might ask.
Return ONLY a JSON array of 5 question strings, nothing else."""

    response = client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=400,
    messages=[{"role": "user", "content": prompt}]
)
    
    text = response.content[0].text.strip()
    # Clean markdown fences
    if text.startswith("```"):
        text = "\n".join(text.split("\n")[1:])
    if text.endswith("```"):
        text = "\n".join(text.split("\n")[:-1])
    
    try:
        questions = json.loads(text)
    except:
        questions = [
            "What is the total count of records?",
            "What are the top 5 values by frequency?",
            "Are there any missing values?",
            "What is the average of numeric columns?",
            "Show me a summary of the data."
        ]
    
    return jsonify({"questions": questions})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
