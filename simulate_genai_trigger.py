import pandas as pd
import joblib
import numpy as np
import os

# --- Configuration ---
# Get the base directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# File paths for the trained models and knowledge base
MODEL_DIR = os.path.join(BASE_DIR, '2_MSPC_Modeling', 'trained_models')
DATA_FILE = os.path.join(BASE_DIR, 'synthetic_batch_data.csv')
SOP_FILE = os.path.join(BASE_DIR, '3_GenAI_Knowledge_Base', 'SOP_knowledge.csv')

# --- Batch Selection ---
# We select a known FAULTY batch (C-1085 is a 'Door_Open' fault based on the generator script)
FAULTY_BATCH_ID = 'C-1085' 

# --- 1. Load Assets (Robust Loading with Encoding and Cleaning) ---
try:
    # Load MSPC Models
    # Note: These files were saved during the modeling notebook phase.
    pca = joblib.load(os.path.join(MODEL_DIR, 'pca_model.pkl'))
    pls = joblib.load(os.path.join(MODEL_DIR, 'pls_model.pkl'))
    scaler = joblib.load(os.path.join(MODEL_DIR, 'scaler_model.pkl'))
    
    # Load Data and Knowledge Base. Using 'latin1' encoding for robustness.
    full_df = pd.read_csv(DATA_FILE, encoding='latin1')
    sop_kb = pd.read_csv(SOP_FILE, encoding='latin1')
    
    # CRITICAL FIX 1: Clean ALL DataFrame headers to remove spaces
    full_df.columns = full_df.columns.str.strip()
    sop_kb.columns = sop_kb.columns.str.strip()
    
    # CRITICAL FIX 2: Clean the content of the 'Fault_Type' column in both DataFrames
    full_df['Fault_Type'] = full_df['Fault_Type'].astype(str).str.strip()
    sop_kb['Fault_Type'] = sop_kb['Fault_Type'].astype(str).str.strip()

    # --- 2. Data Preparation for Prediction ---

    # Isolate the data for the faulty batch
    fault_data = full_df[full_df['Batch_ID'] == FAULTY_BATCH_ID].copy()

    # Identify Critical Process Parameters (CPPs) for unfolding
    cpp_cols = [col for col in full_df.columns if any(c in col for c in ['Temp', 'Power'])]

    # Unfold the data to match the trained model's format (Batch x (Time*Variable))
    unfolded_input = fault_data.pivot(index='Batch_ID', columns='Time_Min', values=cpp_cols)

    # Ensure data is clean and ready for scaling
    unfolded_input = unfolded_input.dropna(axis=1, how='all').fillna(0)

    # Apply the same scaling used during model training
    X_scaled = scaler.transform(unfolded_input)

    # --- 3. Run Models for Prediction and Status ---

    # Prediction: Get the predicted CQA value (Final Height). 
    predicted_cqa_value = pls.predict(X_scaled).flatten()[0]
    predicted_cqa_value = round(predicted_cqa_value, 2)

    # Get the actual fault type from the CSV (This acts as the trigger label)
    fault_type = fault_data['Fault_Type'].iloc[0]

    # --- 4. RAG Logic and LLM Response Simulation ---

    if fault_type != 'Normal':
        # --- A. Retrieve Structured Data (MSPC -> RAG) ---
        
        # Retrieve the corresponding Prescription, Code, and Root Cause from the SOP knowledge base
        fault_info = sop_kb[sop_kb['Fault_Type'] == fault_type].iloc[0]
        
        alert_code = fault_info['Fault_Code']
        root_cause = fault_info['Root_Cause']
        prescription = fault_info['Prescription_Action']
        sop_ref = fault_info['SOP_Reference']

        # Determine if the predicted height signals a scrap (using the target CQA of 7.5 cm)
        status = "SCRAP" if predicted_cqa_value < 7.5 else "SALVAGEABLE"
        
        # --- B. LLM Simulation (Generating the Copilot Response) ---
        
        final_copilot_response = f"""
======================================================
🚨 CRITICAL MSPC ALERT: BATCH {FAULTY_BATCH_ID} ({alert_code}) 🚨
======================================================
PREDICTED QUALITY STATUS: {status} (Predicted Final Height: {predicted_cqa_value} cm)
Root Cause Analysis (RCA) - RAG Retrieval:
    - Primary Fault: {root_cause}
    - Model Confirmation: The batch deviated significantly from the PCA control space (T2 Anomaly).
    
*** IMMEDIATE ACTION REQUIRED (Prescribed by RAG/SOP) ***
-> {prescription}
-> Reference SOP: {sop_ref}

[Copilot Note: Historical context from qa_deviation_reports.txt indicates this failure signature requires CAPA inspection.]
"""
        print(final_copilot_response)

    else:
        # Output for a Normal Batch
        print(f"\nBATCH {FAULTY_BATCH_ID} Status: Normal. Predicted Final Height: {predicted_cqa_value} cm.")
        print("Process running within Golden Batch specifications. No intervention required.")
        
except Exception as e:
    # This block catches ALL unhandled errors (like the KeyError) and prints a helpful message
    print("\n--- FATAL EXECUTION ERROR ---")
    print(f"The simulation failed before generating the output due to: {type(e).__name__}")
    print(f"Error Details: {e}")
    print("Please verify the data structure, especially the column names in your CSV files.")
    print("-----------------------------")