from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, session
import mysql.connector
import os
import re
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Klucz do szyfrowania sesji

def get_db_connection():
    return mysql.connector.connect(
        host="localhost", user="root", password="root", database="catering"
    )

# Funkcja pomocnicza do sprawdzania, czy użytkownik jest zalogowany
def is_logged_in():
    return 'user_id' in session

# Funkcja pomocnicza do pobierania ról użytkownika
def get_user_roles(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT r.nazwa
        FROM uzytkownicy_role ur
        JOIN role r ON ur.rola_id = r.id
        WHERE ur.uzytkownik_id = %s
    """, (user_id,))
    roles = cursor.fetchall()
    conn.close()
    return [role['nazwa'] for role in roles]

# Główna strona
@app.route("/")
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM pozycje_menu")
        items = cursor.fetchall()
    except mysql.connector.Error:
        # Próbujemy inną nazwę tabeli jeśli pierwsza nie istnieje
        items = []
        print("Uwaga: Tabela pozycje_menu nie została znaleziona.")
    conn.close()
    return render_template("index.html", menu=items)

# Rejestracja
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        imie = request.form.get("imie")
        nazwisko = request.form.get("nazwisko")
        email = request.form.get("email")
        haslo = request.form.get("haslo")
        rola_id = request.form.get("rola")
        
        # Walidacja emaila
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return render_template("register.html", message="Niepoprawny format adresu email", message_type="error")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Sprawdzenie, czy email już istnieje
        cursor.execute("SELECT id FROM uzytkownicy WHERE email = %s", (email,))
        if cursor.fetchone():
            conn.close()
            return render_template("register.html", message="Email jest już zajęty", message_type="error")
        
        # Hashowanie hasła
        hashed_password = generate_password_hash(haslo)
        
        # Dodanie użytkownika
        cursor.execute("""
            INSERT INTO uzytkownicy (imie, nazwisko, email, haslo)
            VALUES (%s, %s, %s, %s)
        """, (imie, nazwisko, email, hashed_password))
        conn.commit()
        
        # Pobranie ID nowego użytkownika
        user_id = cursor.lastrowid
        
        # Dodanie roli użytkownika
        cursor.execute("""
            INSERT INTO uzytkownicy_role (uzytkownik_id, rola_id)
            VALUES (%s, %s)
        """, (user_id, rola_id))
        conn.commit()
        
        conn.close()
        
        return redirect(url_for('login', registered=True))
    
    return render_template("register.html")

# Logowanie
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        haslo = request.form.get("password")
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Pobierz użytkownika po emailu
        cursor.execute("SELECT * FROM uzytkownicy WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if not user or not check_password_hash(user['haslo'], haslo):
            conn.close()
            return render_template("login.html", message="Niepoprawny email lub hasło", message_type="error")
        
        # Jeśli dane są poprawne, zaloguj użytkownika
        session['user_id'] = user['id']
        session['user_name'] = f"{user['imie']} {user['nazwisko']}"
        
        # Pobierz role użytkownika
        roles = get_user_roles(user['id'])
        session['user_roles'] = roles
        
        conn.close()
        return redirect(url_for('dashboard'))
    
    # Sprawdź, czy użytkownik właśnie się zarejestrował
    registered = request.args.get('registered')
    if registered:
        return render_template("login.html", message="Rejestracja zakończona pomyślnie. Możesz się teraz zalogować.", message_type="success")
    
    return render_template("login.html")

# Wylogowanie
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('index'))

# Panel użytkownika
@app.route("/dashboard")
def dashboard():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Pobierz dane użytkownika
    cursor.execute("SELECT * FROM uzytkownicy WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    
    # Pobierz role użytkownika
    role = get_user_roles(user_id)
    
    # Pobierz zamówienia użytkownika (jeśli jest klientem)
    zamowienia = []
    if 'klient' in role:
        cursor.execute("""
            SELECT * FROM zamowienia
            WHERE klient_id = %s
            ORDER BY data_realizacji DESC
        """, (user_id,))
        zamowienia = cursor.fetchall()
    
    # Pobierz dostawy (jeśli jest dostawcą)
    dostawy = []
    if 'dostawca' in role:
        cursor.execute("""
            SELECT z.*, kl.imie as klient_imie, kl.nazwisko as klient_nazwisko
            FROM zamowienia z
            JOIN uzytkownicy kl ON z.klient_id = kl.id
            WHERE z.dostawca_id = %s
            ORDER BY z.data_realizacji DESC
        """, (user_id,))
        dostawy = cursor.fetchall()
    
    conn.close()
    
    return render_template("dashboard.html", user=user, role=role, zamowienia=zamowienia, dostawy=dostawy)

# Edycja profilu użytkownika
@app.route("/profile/edit", methods=["GET", "POST"])
def edit_profile():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == "POST":
        imie = request.form.get("imie")
        nazwisko = request.form.get("nazwisko")
        email = request.form.get("email")
        nowe_haslo = request.form.get("nowe_haslo")
        potwierdz_haslo = request.form.get("potwierdz_haslo")
        obecne_haslo = request.form.get("obecne_haslo")
        
        # Pobierz obecne dane użytkownika
        cursor.execute("SELECT * FROM uzytkownicy WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        
        # Sprawdź obecne hasło
        if not check_password_hash(user['haslo'], obecne_haslo):
            conn.close()
            return render_template("edit_profile.html", user=user, 
                                 message="Niepoprawne obecne hasło", message_type="error")
        
        # Walidacja emaila
        if email != user['email']:
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                conn.close()
                return render_template("edit_profile.html", user=user, 
                                     message="Niepoprawny format adresu email", message_type="error")
            
            # Sprawdź, czy nowy email nie jest już zajęty
            cursor.execute("SELECT id FROM uzytkownicy WHERE email = %s AND id != %s", (email, user_id))
            if cursor.fetchone():
                conn.close()
                return render_template("edit_profile.html", user=user, 
                                     message="Ten adres email jest już używany przez innego użytkownika", 
                                     message_type="error")
        
        # Walidacja nowego hasła (jeśli zostało podane)
        if nowe_haslo:
            if len(nowe_haslo) < 6:
                conn.close()
                return render_template("edit_profile.html", user=user, 
                                     message="Nowe hasło musi mieć co najmniej 6 znaków", message_type="error")
            
            if nowe_haslo != potwierdz_haslo:
                conn.close()
                return render_template("edit_profile.html", user=user, 
                                     message="Nowe hasła nie są identyczne", message_type="error")
            
            # Aktualizuj hasło
            hashed_password = generate_password_hash(nowe_haslo)
            cursor.execute("""
                UPDATE uzytkownicy 
                SET imie = %s, nazwisko = %s, email = %s, haslo = %s 
                WHERE id = %s
            """, (imie, nazwisko, email, hashed_password, user_id))
        else:
            # Aktualizuj bez zmiany hasła
            cursor.execute("""
                UPDATE uzytkownicy 
                SET imie = %s, nazwisko = %s, email = %s 
                WHERE id = %s
            """, (imie, nazwisko, email, user_id))
        
        conn.commit()
        
        # Zaktualizuj dane w sesji
        session['user_name'] = f"{imie} {nazwisko}"
        
        conn.close()
        return render_template("edit_profile.html", user={'imie': imie, 'nazwisko': nazwisko, 'email': email}, 
                             message="Profil został pomyślnie zaktualizowany", message_type="success")
    
    # GET - wyświetl formularz edycji
    cursor.execute("SELECT * FROM uzytkownicy WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    return render_template("edit_profile.html", user=user)

@app.route("/api/orders", methods=["GET"])
def get_orders():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            z.id, z.data_realizacji, z.liczba_zestawow, z.preferencje_dietetyczne,
            kl.imie AS klient_imie, kl.nazwisko AS klient_nazwisko,
            ds.imie AS dostawca_imie, ds.nazwisko AS dostawca_nazwisko
        FROM zamowienia z
        LEFT JOIN uzytkownicy kl ON z.klient_id = kl.id
        LEFT JOIN uzytkownicy ds ON z.dostawca_id = ds.id
    """)
    orders = cursor.fetchall()
    conn.close()
    return jsonify(orders)

@app.route("/api/orders", methods=["POST"])
def create_order():
    if not is_logged_in():
        return jsonify({"error": "Nie jesteś zalogowany"}), 401
    
    data = request.json
    klient_id = data.get("klient_id")
    dostawca_id = data.get("dostawca_id")
    data_realizacji = data.get("data_realizacji")
    liczba_zestawow = data.get("liczba_zestawow")
    preferencje_dietetyczne = data.get("preferencje_dietetyczne", "")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO zamowienia (klient_id, dostawca_id, data_realizacji, liczba_zestawow, preferencje_dietetyczne)
        VALUES (%s, %s, %s, %s, %s)
    """, (klient_id, dostawca_id, data_realizacji, liczba_zestawow, preferencje_dietetyczne))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"}), 201

@app.route("/order")
def order_page():
    if not is_logged_in():
        return redirect(url_for('login'))
    return render_template("order.html")

# API: zwraca listę użytkowników wraz z rolami (potrzebne do formularza)
@app.route("/api/users")
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT u.id, u.imie, u.nazwisko,
            GROUP_CONCAT(r.nazwa) AS role
        FROM uzytkownicy u
        JOIN uzytkownicy_role ur ON u.id = ur.uzytkownik_id
        JOIN role r ON ur.rola_id = r.id
        GROUP BY u.id
    """)
    users = cursor.fetchall()
    conn.close()
    return jsonify(users)

# Start aplikacji
if __name__ == "__main__":
    app.run(debug=True)