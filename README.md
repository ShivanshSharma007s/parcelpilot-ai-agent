# ParcelPilot AI Agent

ParcelPilot AI Agent is an internal support and operations chatbot designed for authorized ParcelPilot staff. It allows employees to investigate customer issues, answer policy questions using RAG (Retrieval-Augmented Generation), search agreements, look up structured data (orders, accounts, tickets), and prepare state-changing actions safely.
Try it: https://parcelpilot.pythonanywhere.com/
## Features
- **Natural Language Chatbot**: Ask questions naturally.
- **RAG via BM25**: Retrieves context from PDFs (policies, SOPs, customer agreements) using lightweight lexical search (TF-IDF/BM25).
- **Structured Data Lookups**: Safe, parameterized querying of an SQLite database.
- **Access Control**: Enforces mock authorization based on the logged-in user role.
- **Safe State Changes**: Prepares actions (like escalations) and explicitly requires user confirmation before execution.

## Architecture & Tech Stack
- **Backend**: Python 3, Flask
- **LLM**: Groq API (using Llama 3 70B)
- **Document Parsing**: `pypdf`
- **Retrieval**: `rank-bm25`
- **Database**: SQLite, `pandas` (for initial ingestion)
- **Frontend**: HTML / CSS / Vanilla JS

## Setup and Installation

1. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Mac/Linux
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set your Groq API key:
   Rename `.env.example` to `.env` and insert your API key:
   ```
   GROQ_API_KEY=your_actual_key_here
   ```

## Data Ingestion
Before running the app, you must ingest the provided Excel and PDF files into the SQLite database and the BM25 index. The source data files should be located in the parent directory (`e:\CalAI`).
```bash
python scripts/ingest_data.py
```
This will create `parcelpilot.db` and index files in `retrieval/`.

## Running Locally
Start the Flask application:
```bash
python app.py
```
Open a browser and navigate to `http://localhost:5000`.

## PythonAnywhere Deployment
This application is fully WSGI compatible and lightweight, making it ideal for PythonAnywhere.
1. Upload the project files to PythonAnywhere.
2. In the Web tab, create a new Web App using "Manual configuration" and Python 3.10.
3. Edit the WSGI configuration file to import your Flask `app`:
   ```python
   import sys
   import os
   
   path = '/home/yourusername/parcelpilot-ai-agent'
   if path not in sys.path:
       sys.path.append(path)
       
   from app import app as application
   ```
4. Set the `GROQ_API_KEY` environment variable in the WSGI file or PA interface.
5. Run `python scripts/ingest_data.py` once from a PA bash console.

## Security Considerations
- API keys are managed via environment variables.
- SQL queries use parameterized inputs to prevent injection.
- LLM is not allowed to generate raw SQL.
- Role-based access control prevents unauthorized users from querying other customers' tickets/orders.
- Actions require explicit UI-level confirmation before committing to the database.
