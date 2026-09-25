import psycopg2

# 1. Paste your Neon connection string here
NEON_URI = "postgresql://neondb_owner:npg_XmJVl3ZNir1b@ep-broad-star-b5rnz3ym-pooler.c-7.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

try:
    print("⏳ Attempting to connect to Neon Cloud...")
    # Connect to the cloud database
    conn = psycopg2.connect(NEON_URI)
    cursor = conn.cursor()
    print("✅ Connection Successful!")

    # 2. Test writing data (Create a mock test table)
    print("⏳ Creating a mock test table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS migration_test (
            id SERIAL PRIMARY KEY,
            test_name VARCHAR(50),
            status VARCHAR(20)
        );
    """)
    
    # 3. Insert a sample test row
    print("⏳ Inserting sample data...")
    cursor.execute(
        "INSERT INTO migration_test (test_name, status) VALUES (%s, %s);", 
        ("SQLite Migration Test", "Working!")
    )
    conn.commit()  # Commit saves changes to the cloud

    # 4. Read it back to verify everything is identical
    print("⏳ Reading data back from Neon...")
    cursor.execute("SELECT * FROM migration_test;")
    result = cursor.fetchall()
    print(f"🎉 Successfully fetched test row from Cloud: {result}")

    # 5. Clean up the test table so your database stays pristine
    print("🧹 Cleaning up test table...")
    cursor.execute("DROP TABLE migration_test;")
    conn.commit()
    
    cursor.close()
    conn.close()
    print("\n All systems go! Your Neon configuration is 100% correct.")

except Exception as e:
    print("\n❌ Migration Connection Failed!")
    print(f"Error details: {e}")
