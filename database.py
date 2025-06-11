import mysql.connector
import os
from werkzeug.security import generate_password_hash

def setup_database():
    print("Setting up database...")
    
    # Połącz się do bazy danych
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root"
    )
    
    # Stworzenie obiektu do wykonywania zapytań
    cursor = conn.cursor()
    
    # Odczytaj plik tworzący bazę danych
    with open('init.sql', 'r', encoding='utf-8') as sql_file:
        sql_script = sql_file.read()
    
    # Zahaszowane hasła dla użytkowników
    hashed_passwords = [
        generate_password_hash('tajne1'),
        generate_password_hash('tajne2'),
        generate_password_hash('tajne3')
    ]

    # Podmiana na realne hasła zahaszowane
    sql_script = sql_script.replace(
        "('Klient', 'Jan', 'Kowalski', 'jan.kowalski@example.com', 'haslo123', '123456789', 'ul. Kwiatowa 5'),\n('Dostawca', 'Anna', 'Nowak', 'anna.nowak@example.com', 'haslo456', '987654321', 'ul. Ogrodowa 10'),\n('Administrator', 'Piotr', 'Zielinski', 'piotr.zielinski@example.com', 'haslo789', '555666777', 'ul. Polna 3')",
        f"('Klient', 'Jan', 'Kowalski', 'jan.kowalski@example.com', '{hashed_passwords[0]}', '123456789', 'ul. Kwiatowa 5'),\n('Dostawca', 'Anna', 'Nowak', 'anna.nowak@example.com', '{hashed_passwords[1]}', '987654321', 'ul. Ogrodowa 10'),\n('Administrator', 'Piotr', 'Zielinski', 'piotr.zielinski@example.com', '{hashed_passwords[2]}', '555666777', 'ul. Polna 3')"
    )
    
    # Dzieli cały plik init.sql na osobne komendy tam gdzie jest ;
    statements = sql_script.split(';')
    
    # Wykonanie komend w pliku init.sql
    for statement in statements:
        # Usunięcie niepotrzebnych znaków białych, jeśli linia nie jest pusta to ją wykonaj
        if statement.strip():
            try:
                # Wykonaj polecenie
                cursor.execute(statement)
                # Wyślij do bazy danych
                conn.commit()
            except mysql.connector.Error as err:
                print(f"Error executing statement: {err}")
                print(f"Statement: {statement.strip()[:100]}...")
    
    # Zamknięcie połączenia
    cursor.close()
    conn.close()
    
    print("Database setup complete!")

if __name__ == "__main__":
    setup_database()
