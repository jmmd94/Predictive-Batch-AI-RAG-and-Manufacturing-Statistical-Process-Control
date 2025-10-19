import pandas as pd
import os

# --- Configuration ---
# Set the base directory (where this script is running from)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, '3_GenAI_Knowledge_Base', 'SOP_knowledge.csv')

# --- 1. Define the Clean Knowledge Data ---
# This dictionary contains the raw, clean strings for your RAG knowledge base.
data = {
    'Fault_Type': ['Normal', 'Door_Open', 'Under_Mixed_Batter'],
    'Fault_Code': ['STATUS_OK', 'TEMP_EXCUR_F20', 'MECH_FAILURE_M03'],
    'Root_Cause': [
        'Process running within Golden Batch specifications.',
        'Significant heat loss due to process interruption (Oven Door opened/failed seal). Batter core temperature is critically delayed.',
        'Mechanical issue in the mixing sequence caused heterogeneous material density, resulting in inconsistent heat transfer and uneven curing.'
    ],
    'Prescription_Action': [
        'Continue monitoring process parameters. Log successful batch completion at T=60 minutes.',
        'Initiate emergency bake time extension (SOP-B1) and manually recalibrate oven temp to 185°C for remaining 15 minutes to attempt salvage.',
        'Immediately isolate the batch for inspection. If purity prediction remains below 96.0%, abort the batch and initiate cleaning cycle per SOP-C-010.'
    ],
    'SOP_Reference': ['SOP-QA-001', 'SOP-B-005', 'SOP-QA-003']
}

# --- 2. Create DataFrame and Export ---
try:
    df = pd.DataFrame(data)
    
    # Save the DataFrame as a clean CSV without index numbers
    # Pandas automatically handles quotation marks for cells containing commas.
    df.to_csv(FILE_PATH, index=False, encoding='utf-8')
    
    print(f"\nSUCCESS: SOP knowledge base created at: {FILE_PATH}")

except Exception as e:
    print(f"\nERROR: Failed to create CSV file. Details: {e}")