from flask import Flask, jsonify, render_template
import mysql.connector

# Stworzenie obiektu klasy Flash, naszego "serwera"
app = Flask(__name__)


# Funkcja do łączenia się z bazą danych "catering" z użytkownikiem i hasłem root
def get_db_connection():
    return mysql.connector.connect(
        host="localhost", user="root", password="root", database="catering"
    )


# Gdy ktoś wejdzie w /menu to aplikacja łączy się z bazą danych i pobiera rekordy
# z tabeli menu i zwraca je jako json
@app.route("/menu")
def menu():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM menu")
    items = cursor.fetchall()
    conn.close()
    return jsonify(items)


# Główna strona /, Flask ładuje szablon templates/index.html i zwraca go jako stronę HTML
@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM menu")
    items = cursor.fetchall()
    conn.close()
    return render_template("index.html", menu=items)

# Start aplikacji
if __name__ == "__main__":
    app.run(debug=True)
