import mysql.connector
import os
from werkzeug.security import generate_password_hash

def setup_database():
    print("Setting up database...")
    
    # Połącz się do bazy danych
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root"
    )
    
    # Stworzenie obiektu do wykonywania zapytań
    cursor = conn.cursor()
    
    # Odczytaj plik tworzący bazę danych
    with open('init.sql', 'r') as sql_file:
        sql_script = sql_file.read()
    
    # Zahaszowane hasła dla użytkowników
    hashed_passwords = [
        generate_password_hash('tajne1'),
        generate_password_hash('tajne2'),
        generate_password_hash('tajne3')
    ]

    # Podmiana na realne hasła zahaszowane
    sql_script = sql_script.replace(
        "('Jan', 'Kowalski', 'jan.kowalski@example.com', '%s'),\n('Anna', 'Nowak', 'anna.nowak@example.com', '%s'),\n('Piotr', 'Zielinski', 'piotr.zielinski@example.com', '%s')",
        f"('Jan', 'Kowalski', 'jan.kowalski@example.com', '{hashed_passwords[0]}'),\n('Anna', 'Nowak', 'anna.nowak@example.com', '{hashed_passwords[1]}'),\n('Piotr', 'Zielinski', 'piotr.zielinski@example.com', '{hashed_passwords[2]}')"
    )
    
    # Dzieli cały plik init.sql na osobne komendy tam gdzie jest ;
    statements = sql_script.split(';')
    
    # Wykonanie komend w pliki init.sql
    for statement in statements:
        # Usunięcie nie potrzebnych zanków białych, jeśli linia nie jest pusta to ją wykonaj
        if statement.strip():
            try:
                # Wykonaj polecenie
                cursor.execute(statement)
                # Wyślij do bazy danych
                conn.commit()
            except mysql.connector.Error as err:
                print(f"Error executing statement: {err}")
                print(f"Statement: {statement[:100]}...")
    
    # Zamknięcie połączenia
    cursor.close()
    conn.close()
    
    print("Database setup complete!")

if __name__ == "__main__":
    setup_database()