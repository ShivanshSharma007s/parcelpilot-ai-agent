import os
import sys
import pandas as pd
from pypdf import PdfReader
import pickle
import json
from rank_bm25 import BM25Okapi

# Add parent dir to path to import config and db
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATA_DIR, INDEX_PATH, DOC_CHUNKS_PATH
from database.db import get_db_connection, init_db

def ingest_structured_data():
    print("Ingesting structured data...")
    excel_path = os.path.join(DATA_DIR, "ParcelPilot_Assessment_Data.xlsx")
    if not os.path.exists(excel_path):
        print(f"Error: {excel_path} not found.")
        return

    init_db()
    conn = get_db_connection()
    
    # Read sheets
    df_accounts = pd.read_excel(excel_path, sheet_name="accounts")
    df_orders = pd.read_excel(excel_path, sheet_name="orders")
    df_tickets = pd.read_excel(excel_path, sheet_name="tickets")
    
    # Replace NaN with None for SQLite insertion
    df_accounts = df_accounts.where(pd.notnull(df_accounts), None)
    df_orders = df_orders.where(pd.notnull(df_orders), None)
    df_tickets = df_tickets.where(pd.notnull(df_tickets), None)
    
    # Insert accounts
    for _, row in df_accounts.iterrows():
        conn.execute("""
            INSERT INTO accounts (account_id, account_name, plan, status, csm, contract_file, premium_support, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, tuple(row))
        
    # Insert orders
    for _, row in df_orders.iterrows():
        conn.execute("""
            INSERT INTO orders (order_id, account_id, carrier, status, booked_at, pickup_window_start, pickup_window_end, pickup_actual_at, shipment_fee_inr, carrier_fault, customer_fault, cancellation_requested_at, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, tuple(row))
        
    # Insert tickets
    for _, row in df_tickets.iterrows():
        conn.execute("""
            INSERT INTO tickets (ticket_id, account_id, created_at, status, subject, description, channel, assigned_to, last_customer_message_at, historical_resolution)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, tuple(row))
        
    conn.commit()
    conn.close()
    print("Structured data ingested successfully.")

def process_pdf(filepath):
    filename = os.path.basename(filepath)
    reader = PdfReader(filepath)
    
    # Determine metadata based on filename
    status = "Current"
    authority = "Medium"
    customer = None
    
    if "DEPRECATED" in filename:
        status = "Deprecated"
        authority = "Low"
    elif "CURRENT" in filename or "SOP" in filename:
        authority = "High"
        
    if "Northstar" in filename:
        authority = "Very High (Customer Specific)"
        customer = "Northstar Logistics"
    elif "LumenWorks" in filename:
        authority = "Very High (Customer Specific)"
        customer = "LumenWorks"
        
    chunks = []
    
    for page_num, page in enumerate(reader.pages):
        text = page.extract_text()
        if not text:
            continue
            
        paragraphs = text.split('\n\n')
        current_chunk = []
        current_len = 0
        
        for p in paragraphs:
            p = p.strip()
            if not p:
                continue
            current_chunk.append(p)
            current_len += len(p)
            
            if current_len > 1000:  # Roughly chunk size
                chunk_text = "\n".join(current_chunk)
                chunks.append({
                    "text": chunk_text,
                    "metadata": {
                        "filename": filename,
                        "page": page_num + 1,
                        "status": status,
                        "authority": authority,
                        "customer": customer
                    }
                })
                current_chunk = []
                current_len = 0
                
        if current_chunk:
            chunk_text = "\n".join(current_chunk)
            chunks.append({
                "text": chunk_text,
                "metadata": {
                    "filename": filename,
                    "page": page_num + 1,
                    "status": status,
                    "authority": authority,
                    "customer": customer
                }
            })
            
    return chunks

def ingest_documents():
    print("Ingesting documents...")
    all_chunks = []
    
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".pdf"):
            filepath = os.path.join(DATA_DIR, filename)
            chunks = process_pdf(filepath)
            all_chunks.extend(chunks)
            
    if not all_chunks:
        print("No PDFs found.")
        return
        
    # Build BM25 index
    print("Building BM25 index...")
    tokenized_corpus = [chunk["text"].lower().split() for chunk in all_chunks]
    bm25 = BM25Okapi(tokenized_corpus)
    
    os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
    
    with open(INDEX_PATH, 'wb') as f:
        pickle.dump(bm25, f)
        
    with open(DOC_CHUNKS_PATH, 'wb') as f:
        pickle.dump(all_chunks, f)
        
    print(f"Indexed {len(all_chunks)} chunks from documents.")

if __name__ == "__main__":
    ingest_structured_data()
    ingest_documents()
    print("Ingestion complete!")
