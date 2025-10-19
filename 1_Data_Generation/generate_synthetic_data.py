import pandas as pd
import numpy as np

# --- 1. CONFIGURATION AND PARAMETERS ---
# Define batch parameters
N_NORMAL_BATCHES = 80
N_FAULT_BATCHES_DOOR = 10
N_FAULT_BATCHES_MIXING = 10
TOTAL_BATCHES = N_NORMAL_BATCHES + N_FAULT_BATCHES_DOOR + N_FAULT_BATCHES_MIXING
TIME_STEPS = 60  # 1 hour run, sampled every 1 minute
TIME_INTERVAL = 1  # minutes

# Golden Batch Targets (Process Control Points - CPPs)
TEMP_TARGET = 175.0  # Oven Setpoint in Celsius
TEMP_NOISE = 0.5     # Standard deviation for normal fluctuation
BATTER_TEMP_START = 25.0
BATTER_TEMP_END = 95.0
STIRRER_POWER_BASE = 5.0 # Base power (kW)
STIRRER_POWER_PEAK = 20.0 # Peak power (kW)

# Golden Batch Targets (Quality Attributes - CQAs)
CQA_HEIGHT_TARGET = 8.0
CQA_MOISTURE_TARGET = 18.0
CQA_DONENESS_PERFECT = 1.0

# --- 2. CORE FUNCTIONS ---

def create_golden_batch_profile(time_steps):
    """Generates the ideal time-series trajectory."""
    time = np.arange(0, time_steps * TIME_INTERVAL, TIME_INTERVAL)

    # 1. Oven Temperature (Stays around setpoint with noise)
    oven_temp_profile = np.full(time_steps, TEMP_TARGET) + np.random.normal(0, TEMP_NOISE, time_steps)

    # 2. Batter Center Temperature (Linear ramp from 25C to 95C)
    batter_temp_profile = np.linspace(BATTER_TEMP_START, BATTER_TEMP_END, time_steps) + np.random.normal(0, 0.2, time_steps)

    # 3. Stirrer Power (Ramps up as viscosity/setting occurs)
    # Using a simple linear ramp for power based on time.
    power_ramp = np.linspace(STIRRER_POWER_BASE, STIRRER_POWER_PEAK, time_steps)
    stirrer_power_profile = power_ramp + np.random.normal(0, 0.5, time_steps)

    return pd.DataFrame({
        'Time_Min': time,
        'Oven_Temp_Actual': oven_temp_profile,
        'Batter_Center_Temp': batter_temp_profile,
        'Stirrer_Power_Online': stirrer_power_profile
    })

def calculate_cqa_values(profile_df, fault_type):
    """Calculates final CQA values based on the process profile and fault type."""
    
    # Base Case (High Quality)
    final_cqa = {
        'Final_Height': np.random.uniform(CQA_HEIGHT_TARGET - 0.2, CQA_HEIGHT_TARGET + 0.2),
        'Final_Moisture': np.random.uniform(CQA_MOISTURE_TARGET - 0.5, CQA_MOISTURE_TARGET + 0.5),
        'Internal_Doneness': CQA_DONENESS_PERFECT
    }
    
    # Introduce Fault Effects (Scrap batches)
    if fault_type == 'Door_Open':
        # Severe cold exposure results in low height and high doneness score (raw core)
        final_cqa['Final_Height'] = np.random.uniform(6.5, 7.0)
        final_cqa['Internal_Doneness'] = np.random.uniform(3.5, 4.5)
        final_cqa['Final_Moisture'] = np.random.uniform(19.0, 21.0) # High moisture in the center
    
    elif fault_type == 'Under_Mixed_Batter':
        # Poor mixing/inconsistent heat transfer results in low height and uneven moisture
        final_cqa['Final_Height'] = np.random.uniform(6.0, 6.7)
        final_cqa['Final_Moisture'] = np.random.uniform(20.0, 22.0)
        final_cqa['Internal_Doneness'] = np.random.uniform(2.5, 3.5)
        
    return final_cqa

def inject_fault(df, fault_type):
    """Applies the specific time-series deviation for the fault type."""
    
    # --- 1. Apply Process Deviations ---
    if fault_type == 'Door_Open':
        start_time, end_time = 20, 30
        
        # 35C drop in oven temp for the 10-minute window
        df.loc[(df['Time_Min'] >= start_time) & (df['Time_Min'] <= end_time), 'Oven_Temp_Actual'] -= 35.0 
        
        # Batter center temperature slows down dramatically
        df.loc[(df['Time_Min'] > start_time), 'Batter_Center_Temp'] = df.loc[(df['Time_Min'] > start_time), 'Batter_Center_Temp'].apply(lambda x: x - np.random.uniform(10, 15))
    
    elif fault_type == 'Under_Mixed_Batter':
        start_time, end_time = 5, 15
        
        # Simulate a sudden drop in mixing power (kW)
        df.loc[(df['Time_Min'] >= start_time) & (df['Time_Min'] <= end_time), 'Stirrer_Power_Online'] -= 7.0
        
    # --- 2. Calculate Final CQAs ---
    final_cqa_values = calculate_cqa_values(df, fault_type)
    
    # Append the CQA values only to the last time step (Time_Min 59)
    df.loc[df.index[-1], ['Final_Height', 'Final_Moisture', 'Internal_Doneness']] = final_cqa_values.values()
    df['Fault_Type'] = fault_type
    
    return df

# --- 3. EXECUTION BLOCK ---

if __name__ == '__main__':
    all_batches = []
    batch_counter = 1001

    fault_scenarios = (
        ['Normal'] * N_NORMAL_BATCHES + 
        ['Door_Open'] * N_FAULT_BATCHES_DOOR + 
        ['Under_Mixed_Batter'] * N_FAULT_BATCHES_MIXING
    )
    
    for fault_type in fault_scenarios:
        # 1. Create the ideal baseline profile
        baseline = create_golden_batch_profile(TIME_STEPS)
        
        # 2. Inject the fault or maintain normal variance
        batch_data = inject_fault(baseline.copy(), fault_type)
        
        # 3. Assign Batch ID
        batch_data['Batch_ID'] = f'C-{batch_counter}'
        all_batches.append(batch_data)
        batch_counter += 1

    # Combine all batches into one large DataFrame
    final_df = pd.concat(all_batches).fillna(np.nan)

    # --- Export ---
    # Save the data one level up in the repository root for easy access
    final_df.to_csv('synthetic_batch_data.csv', index=False)

    print(f"Generated {TOTAL_BATCHES} batches with {TIME_STEPS} time steps each.")
    print("File 'synthetic_batch_data.csv' exported successfully to the root directory.")