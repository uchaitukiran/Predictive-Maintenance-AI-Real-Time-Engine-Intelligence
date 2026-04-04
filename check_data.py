import sqlite3

try:
    conn = sqlite3.connect('engine_data.db')
    cursor = conn.cursor()
    
    # This magic command lists all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("------------------------------------------------")
    print("✅ TABLES FOUND IN YOUR DATABASE:")
    for table in tables:
        print(f"   -> {table[0]}")
    print("------------------------------------------------")
    
    conn.close()
except Exception as e:
    print(f"❌ Error: {e}")