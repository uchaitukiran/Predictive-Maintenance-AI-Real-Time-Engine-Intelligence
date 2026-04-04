import sqlite3

try:
    conn = sqlite3.connect('engine_data.db')
    cursor = conn.cursor()
    
    # Get column names
    cursor.execute("PRAGMA table_info(predictions);")
    columns = cursor.fetchall()
    
    print("------------------------------------------------")
    print("✅ COLUMNS IN 'predictions' TABLE:")
    for col in columns:
        print(f"   -> {col[1]}") # col[1] is the name
    print("------------------------------------------------")
    
    # Get one row of data
    cursor.execute("SELECT * FROM predictions LIMIT 1;")
    row = cursor.fetchone()
    print("SAMPLE ROW:", row)
    
    conn.close()
except Exception as e:
    print(f"❌ Error: {e}")