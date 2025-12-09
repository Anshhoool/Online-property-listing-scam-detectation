import sqlite3

# Connect - creates file if not exists
conn = sqlite3.connect('listings.db')
c = conn.cursor()

# Create table
c.execute('''
CREATE TABLE IF NOT EXISTS listings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    price TEXT,
    beds TEXT,
    baths TEXT,
    description TEXT,
    image TEXT,
    contact_email TEXT
)
''')

conn.commit()
conn.close()
print("✅ Database and table created successfully!")
