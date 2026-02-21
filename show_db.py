import sqlite3

# Connect to database
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Show tables
print("=== TABLES IN DATABASE ===\n")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
for table in tables:
    print(f"- {table[0]}")

# Show schemes count
print("\n=== SCHEMES ===")
cursor.execute("SELECT COUNT(*) FROM schemes")
print(f"Total schemes: {cursor.fetchone()[0]}")

# Show sample schemes
cursor.execute("SELECT id, name, category FROM schemes LIMIT 5")
print("\nSample schemes:")
for row in cursor.fetchall():
    print(f"  {row[0]}. {row[1]} ({row[2]})")

# Show users count
print("\n=== USERS ===")
cursor.execute("SELECT COUNT(*) FROM users")
print(f"Total users: {cursor.fetchone()[0]}")

conn.close()
