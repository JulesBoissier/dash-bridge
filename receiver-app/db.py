import os
import psycopg2
from psycopg2.extras import RealDictCursor

# Database connection string
connection_string = os.environ.get("DATABASE_URL", "postgresql://postgres:docker@127.0.0.1:5432")

def get_db_connection():
    """Get database connection"""
    try:
        conn = psycopg2.connect(connection_string)
        return conn
    except psycopg2.OperationalError as e:
        print(f"Database connection error (OperationalError): {e}")
        return None
    except Exception as e:
        print(f"Database connection error (Other): {type(e).__name__}: {e}")
        return None

def init_database():
    """Initialize database table if it doesn't exist"""
    print(f"Attempting to connect to database: {connection_string}")
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            print("Connected to database successfully")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS user_entries (
                    id SERIAL PRIMARY KEY,
                    app_name VARCHAR(255) NOT NULL,
                    username VARCHAR(255) NOT NULL,
                    timestamp VARCHAR(50) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
            print("Database table initialized successfully")
            
            # Verify table was created
            cur.execute("SELECT COUNT(*) FROM user_entries;")
            count = cur.fetchone()[0]
            print(f"Table verification: found {count} existing entries")
            
        except Exception as e:
            print(f"Database initialization error: {e}")
            print(f"Error details: {type(e).__name__}: {str(e)}")
        finally:
            cur.close()
            conn.close()
    else:
        print("Failed to connect to database during initialization")

def get_all_entries():
    """Get all entries from database"""
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("SELECT app_name, username, timestamp FROM user_entries ORDER BY created_at DESC")
            entries = cur.fetchall()
            return [dict(entry) for entry in entries]
        except Exception as e:
            print(f"Error fetching entries: {e}")
            return []
        finally:
            cur.close()
            conn.close()
    return []

def add_entry_to_db(app_name, username, timestamp):
    """Add entry to database"""
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO user_entries (app_name, username, timestamp) VALUES (%s, %s, %s)",
                (app_name, username, timestamp)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error adding entry to database: {e}")
            return False
        finally:
            cur.close()
            conn.close()
    return False

def clear_all_entries():
    """Clear all entries from database"""
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM user_entries")
            conn.commit()
            rows_affected = cur.rowcount
            print(f"Cleared {rows_affected} entries from database")
            return True
        except Exception as e:
            print(f"Error clearing database: {e}")
            return False
        finally:
            cur.close()
            conn.close()
    return False 