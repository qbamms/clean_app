import sqlite3
import psycopg2

# 1. Connect to your local SQLite database file
sqlite_conn = sqlite3.connect('db/cleaning_engine.db')
sqlite_cursor = sqlite_conn.cursor()

# 2. Connect to your new Free Cloud Postgres database
POSTGRES_URI = "postgresql://neondb_owner:npg_XmJVl3ZNir1b@ep-broad-star-b5rnz3ym-pooler.c-7.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
pg_conn = psycopg2.connect(POSTGRES_URI)
pg_cursor = pg_conn.cursor()

# Get a list of all tables in your SQLite database
sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [row[0] for row in sqlite_cursor.fetchall() if row[0] != 'sqlite_sequence']

print(f"Found {len(tables)} tables to migrate: {tables}")

print(f"🚀 Starting auto-migration for tables: {tables}")

# Type mapping from SQLite to PostgreSQL
TYPE_MAP = {
    'INTEGER': 'INTEGER',
    'INT': 'INTEGER',
    'TEXT': 'TEXT',
    'BLOB': 'BYTEA',
    'REAL': 'DOUBLE PRECISION',
    'NUMERIC': 'NUMERIC',
    '': 'TEXT'  # Default fallback if SQLite type is empty
}

for table_tuple in tables:
    table = table_tuple
    print(f"Migrating table: {table}...")

    #  Read table layout (columns) from SQLite
    sqlite_cursor.execute(f"PRAGMA table_info({table});")
    columns_info = sqlite_cursor.fetchall()

    # Dynamically build the PostgreSQL CREATE TABLE query
    pg_columns = []
    col_names = []
    pk_columns = []

    for col in columns_info:
        # col structure: (cid, name, type, notnull, dflt_value, pk)
        col_name = col[1]
        sqlite_type = col[2].upper()
        is_pk = col[5]

        # Clean up types with lengths (e.g., VARCHAR(255) -> TEXT for simplicity in Postgres)
        base_type = sqlite_type.split('(')[0].strip()
        pg_type = TYPE_MAP.get(base_type, 'TEXT')
        
        col_def = f'"{col_name}" {pg_type}'
        pg_columns.append(col_def)
        col_names.append(f'"{col_name}"')

        if is_pk:
            pk_columns.append(f'"{col_name}"')
            
     # Handle composite primary keys or single primary keys safely for Postgres
    if pk_columns:
        pk_constraint = f"PRIMARY KEY ({', '.join(pk_columns)})"
        pg_columns.append(pk_constraint)

    create_table_query = f'CREATE TABLE IF NOT EXISTS "{table}" (\n  ' + ",\n  ".join(pg_columns) + "\n);"

    # Create the table in Neon
    try:
        pg_cursor.execute(create_table_query)
        pg_conn.commit()
        print(f"  ✅ Table structure created/verified in Neon.")
    except Exception as e:
        pg_conn.rollback()
        print(f"  ❌ Failed to create table schema for {table}: {e}")
        continue

    # 6. Fetch and insert the data rows
    sqlite_cursor.execute(f'SELECT * FROM "{table}";')
    rows = sqlite_cursor.fetchall()
    
    if not rows:
        print(f"  ℹ️ Table '{table}' is empty. No data to migrate.")
        continue

     # Dynamically build the INSERT statement
    placeholders = ", ".join(["%s"] * len(col_names))
    insert_query = f'INSERT INTO "{table}" ({", ".join(col_names)}) VALUES ({placeholders});'
    
    # Check if table already has rows to prevent duplicate error loops on primary keys
    pg_cursor.execute(f'SELECT COUNT(*) FROM "{table}";')
    if pg_cursor.fetchone()[0] > 0:
        print(f"  ⚠️ Warning: Cloud table '{table}' already contains data. Skipping row insertion to prevent conflicts.")
        continue

    try:
        pg_cursor.executemany(insert_query, rows)
        pg_conn.commit()
        print(f"  🎉 Successfully migrated {len(rows)} rows into '{table}'!")
    except Exception as e:
        pg_conn.rollback()
        print(f"  ❌ Error copying rows for {table}: {e}")

# Clean up connections
sqlite_conn.close()
pg_conn.close()
print("\n🏁 Auto-migration process complete!")