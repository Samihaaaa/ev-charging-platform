"""
Database migration script to add created_at column to bookings table
"""

import sqlite3
import os
from datetime import datetime

def add_created_at_column():
    """Add created_at column to bookings table if it doesn't exist"""
    
    db_path = os.path.join(os.path.dirname(__file__), 'ev.db')
    
    if not os.path.exists(db_path):
        print("Database file not found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if created_at column exists
        cursor.execute("PRAGMA table_info(bookings)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'created_at' not in columns:
            print("Adding created_at column to bookings table...")
            cursor.execute("ALTER TABLE bookings ADD COLUMN created_at DATETIME")
            
            # Update existing bookings with current timestamp
            current_time = datetime.now().isoformat()
            cursor.execute("UPDATE bookings SET created_at = ? WHERE created_at IS NULL", (current_time,))
            
            conn.commit()
            print("created_at column added successfully!")
        else:
            print("created_at column already exists!")
        
        # Verify the column was added
        cursor.execute("PRAGMA table_info(bookings)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"Current columns: {columns}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error adding created_at column: {e}")
        return False

if __name__ == "__main__":
    add_created_at_column()
