import pandas as pd
import random
import os

def generate_engine_logs(num_logs=2000):
    """
    Generates AUGMENTED synthetic engine logs (with typos and variations)
    to make the model robust.
    """
    
    # AUGMENTED TEMPLATES (Added typos, slang, variations)
    
    normal_templates = [
        "Engine {} operating normally. All systems nominal.",
        "Cycle {}: Standard pressure readings. Temperature stable.",
        "Routine check for Engine {}: No anomalies detected.",
        "Engine {} performance optimal. Fuel efficiency at 98%.",
        # VARIATIONS:
        "Eng {} is runnin smooth.", # Typo
        "System {} nominal. All good.", 
        "Check complete: Engine {} is fine.",
        "Normal operation for engine {}.",
        "Performance {} is optimal."
    ]
    
    warning_templates = [
        "WARNING: Engine {} vibration levels slightly elevated at cycle {}.",
        "Alert: Sensor {} reporting fluctuating readings. Check connection.",
        "Engine {} oil temperature rising above normal threshold.",
        "Minor pressure drop detected in Engine {} combustion chamber.",
        "Advisory: Engine {} turbine efficiency decreased by 2%.",
        # VARIATIONS (The critical fix for your input):
        "Engine {} is getting hot.", # Simple version
        "Why is engine {} very hot?", # Question format
        "Temp rising for eng {}.", # Typo/Short
        "Engine {} overheating warning.", # Keyword variation
        "High temp alert for {}.", 
        "Sensor {} says its too hot.",
        "Engine {} temp is high." 
    ]
    
    critical_templates = [
        "CRITICAL: Engine {} fire detected in combustion chamber! Emergency shutdown initiated.",
        "FAILURE: Engine {} turbine blade fracture detected. Immediate inspection required.",
        "EMERGENCY: Engine {} total pressure loss. System failure imminent.",
        "CRITICAL ALERT: Engine {} exhaust gas temperature exceeding safety limits!",
        "FATAL ERROR: Engine {} sensor array offline. Control system compromised.",
        # VARIATIONS:
        "FIRE! Engine {} is burning!",
        "Explosion risk in engine {}!",
        "Engine {} failed completely.",
        "Critical failure for {}.",
        "Engine {} is on fire!",
        "Emergency stop for engine {}."
    ]
    
    logs = []
    labels = []
    
    print(f"⚙️ Generating {num_logs} AUGMENTED engine logs...")
    
    for i in range(num_logs):
        engine_id = f"ENG-{random.randint(100, 999)}"
        cycle = random.randint(1, 500)
        
        rand_val = random.random()
        
        if rand_val < 0.60: 
            template = random.choice(normal_templates)
            label = "NORMAL"
        elif rand_val < 0.90: 
            template = random.choice(warning_templates)
            label = "WARNING"
        else: 
            template = random.choice(critical_templates)
            label = "CRITICAL"
            
        # Fill template
        # Handle templates that need 2 args vs 1 arg
        try:
            if "{}" in template and template.count("{}") == 2:
                log_message = template.format(engine_id, cycle)
            else:
                log_message = template.format(engine_id)
        except:
            log_message = template # Fallback
            
        logs.append(log_message)
        labels.append(label)
        
    # Create DataFrame
    df = pd.DataFrame({
        'log_message': logs,
        'status': labels
    })
    
    # Save to CSV
    output_path = os.path.join('data', 'raw', 'engine_logs.csv')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    
    print(f"✅ SUCCESS: Generated logs saved to {output_path}")
    print(df['status'].value_counts())

if __name__ == "__main__":
    generate_engine_logs(num_logs=3000) # Increased count