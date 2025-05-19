import mysql.connector
import os
from werkzeug.security import generate_password_hash

def setup_database():
    print("Setting up database...")
    
    # Connect to MySQL server without specifying a database
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root"
    )
    
    cursor = conn.cursor()
    
    # Read the SQL file
    with open('init.sql', 'r') as sql_file:
        sql_script = sql_file.read()
    
    # Hash passwords for initial users
    hashed_passwords = [
        generate_password_hash('tajne1'),
        generate_password_hash('tajne2'),
        generate_password_hash('tajne3')
    ]
    
    # Replace placeholders with hashed passwords
    sql_script = sql_script.replace(
        "('Jan', 'Kowalski', 'jan.kowalski@example.com', '%s'),\n('Anna', 'Nowak', 'anna.nowak@example.com', '%s'),\n('Piotr', 'Zielinski', 'piotr.zielinski@example.com', '%s')",
        f"('Jan', 'Kowalski', 'jan.kowalski@example.com', '{hashed_passwords[0]}'),\n('Anna', 'Nowak', 'anna.nowak@example.com', '{hashed_passwords[1]}'),\n('Piotr', 'Zielinski', 'piotr.zielinski@example.com', '{hashed_passwords[2]}')"
    )
    
    # Split the SQL script into individual statements
    statements = sql_script.split(';')
    
    # Execute each statement
    for statement in statements:
        if statement.strip():
            try:
                cursor.execute(statement)
                conn.commit()
            except mysql.connector.Error as err:
                print(f"Error executing statement: {err}")
                print(f"Statement: {statement[:100]}...")
    
    # Close connection
    cursor.close()
    conn.close()
    
    print("Database setup complete!")

if __name__ == "__main__":
    setup_database()