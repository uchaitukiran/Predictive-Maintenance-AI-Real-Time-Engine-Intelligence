import sqlite3

print("\n--- Reading Database ---")
try:
    conn = sqlite3.connect('engine_data.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM predictions")
    rows = cursor.fetchall()
    
    if not rows:
        print("No data found in database.")
    else:
        for row in rows:
            print(row)
            
    conn.close()
except Exception as e:
    print(f"Error: {e}")