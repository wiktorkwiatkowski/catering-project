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

# Funkcja pomocnicza do pobierania roli użytkownika (ENUM)
def get_user_role(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT rola FROM uzytkownik WHERE id = %s", (user_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result['rola']
    else:
        return None

# Główna strona
@app.route("/")
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Pobierz dostępne opcje dietetyczne
    cursor.execute("SELECT * FROM opcja_dietetyczna")
    opcje = cursor.fetchall()

    conn.close()
    return render_template("index.html", opcje=opcje)

# Rejestracja
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        imie = request.form.get("imie")
        nazwisko = request.form.get("nazwisko")
        email = request.form.get("email")
        haslo = request.form.get("haslo")
        telefon = request.form.get("telefon")
        adres = request.form.get("adres")
        miejscowosc = request.form.get("miejscowosc")
        kod_pocztowy = request.form.get("kod_pocztowy")
        nr_domu = request.form.get("nr_domu")

        # Walidacja kodu pocztowego
        if not re.match(r"^\d{2}-\d{3}$", kod_pocztowy):
            return render_template("register.html", message="Niepoprawny format kodu pocztowego (wymagany format: XX-XXX)", message_type="error")
        
        # Walidacja emaila
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return render_template("register.html", message="Niepoprawny format adresu email", message_type="error")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Sprawdzenie, czy email już istnieje
        cursor.execute("SELECT id FROM uzytkownik WHERE email = %s", (email,))
        if cursor.fetchone():
            conn.close()
            return render_template("register.html", message="Email jest już zajęty", message_type="error")
        
        # Hashowanie hasła
        hashed_password = generate_password_hash(haslo)
        
        # Dodanie użytkownika → rola zawsze 'Klient'
        cursor.execute("""
        INSERT INTO uzytkownik (rola, imie, nazwisko, email, haslo, numer_telefonu, adres, miejscowosc, kod_pocztowy, nr_domu)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, ('Klient', imie, nazwisko, email, hashed_password, telefon, adres, miejscowosc, kod_pocztowy, nr_domu))
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
        cursor.execute("SELECT * FROM uzytkownik WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if not user or not check_password_hash(user['haslo'], haslo):
            conn.close()
            return render_template("login.html", message="Niepoprawny email lub hasło", message_type="error")
        
        # Jeśli dane są poprawne, zaloguj użytkownika
        session['user_id'] = user['id']
        session['user_name'] = f"{user['imie']} {user['nazwisko']}"
        session['user_role'] = get_user_role(user['id'])
        
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
    cursor.execute("SELECT * FROM uzytkownik WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    
    # Pobierz role użytkownika
    role = get_user_role(user_id)
    
    # Pobierz zamówienia użytkownika (jeśli jest klientem)
    zamowienia = []
    if role == 'Klient':
        cursor.execute("""
            SELECT * FROM zamowienie
            WHERE uzytkownik_id = %s
            ORDER BY data_dostawy DESC
        """, (user_id,))
        zamowienia = cursor.fetchall()
    
    # Pobierz dostawy (jeśli jest dostawcą)
    dostawy = []
    if role == 'Dostawca':
        cursor.execute("""
            SELECT z.*, kl.imie as klient_imie, kl.nazwisko as klient_nazwisko
            FROM zamowienie z
            JOIN uzytkownik kl ON z.uzytkownik_id = kl.id
            WHERE z.dostawca_id = %s
            ORDER BY z.data_dostawy DESC
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
        telefon = request.form.get("telefon")
        adres = request.form.get("adres")
        miejscowosc = request.form.get("miejscowosc")
        kod_pocztowy = request.form.get("kod_pocztowy")
        nr_domu = request.form.get("nr_domu")
        email = request.form.get("email")
        nowe_haslo = request.form.get("nowe_haslo")
        potwierdz_haslo = request.form.get("potwierdz_haslo")
        obecne_haslo = request.form.get("obecne_haslo")
        
        # Pobierz obecne dane użytkownika
        cursor.execute("SELECT * FROM uzytkownik WHERE id = %s", (user_id,))
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
            cursor.execute("SELECT id FROM uzytkownik WHERE email = %s AND id != %s", (email, user_id))
            if cursor.fetchone():
                conn.close()
                return render_template("edit_profile.html", user=user, 
                                     message="Ten adres email jest już używany przez innego użytkownika", 
                                     message_type="error")
        # Walidacja kodu pocztowego
        if not re.match(r"^\d{2}-\d{3}$", kod_pocztowy):
            cursor.execute("SELECT * FROM uzytkownik WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            conn.close()
            return render_template("edit_profile.html", user=user, 
                                        message="Niepoprawny format kodu pocztowego (wymagany format: XX-XXX)", message_type="error")


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
            
            # Aktualizuj hasło + telefon + adres
            hashed_password = generate_password_hash(nowe_haslo)
            cursor.execute("""
                UPDATE uzytkownik 
                SET imie = %s, nazwisko = %s, email = %s, haslo = %s, numer_telefonu = %s, adres = %s, miejscowosc = %s, kod_pocztowy = %s, nr_domu = %s
                WHERE id = %s
            """, (imie, nazwisko, email, hashed_password, telefon, adres, miejscowosc, kod_pocztowy, nr_domu, user_id))
        else:
            # Aktualizuj bez zmiany hasła, ale z telefonem i adresem
            cursor.execute("""
                UPDATE uzytkownik 
                SET imie = %s, nazwisko = %s, email = %s, numer_telefonu = %s, adres = %s, miejscowosc = %s, kod_pocztowy = %s, nr_domu = %s
                WHERE id = %s
            """, (imie, nazwisko, email, telefon, adres, miejscowosc, kod_pocztowy, nr_domu, user_id))
        
        conn.commit()
        
        # Zaktualizuj dane w sesji
        session['user_name'] = f"{imie} {nazwisko}"
        
        conn.close()
        return render_template("edit_profile.html", user={
            'imie': imie,
            'nazwisko': nazwisko,
            'email': email,
            'numer_telefonu': telefon,
            'adres': adres,
            'miejscowosc': miejscowosc,
            'kod_pocztowy': kod_pocztowy,
            'nr_domu': nr_domu
        }, message="Profil został pomyślnie zaktualizowany", message_type="success")
    
    # GET - wyświetl formularz edycji
    cursor.execute("SELECT * FROM uzytkownik WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    return render_template("edit_profile.html", user=user)


# Wyświetlenie menu dla opcji dietetycznej
@app.route("/menu/<int:opcja_id>")
def show_menu_for_option(opcja_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Pobierz nazwę opcji dietetycznej
    cursor.execute("SELECT dieta, opis FROM opcja_dietetyczna WHERE id = %s", (opcja_id,))
    opcja = cursor.fetchone()

    if not opcja:
        conn.close()
        return "Opcja dietetyczna nie istnieje", 404

    # Pobierz pozycje menu powiązane z tą opcją dietetyczną (przez tabela `menu`)
    cursor.execute("""
        SELECT pm.* 
        FROM pozycje_menu pm
        JOIN menu m ON pm.menu_id = m.id
        WHERE m.opcja_dietetyczna_id = %s
    """, (opcja_id,))
    items = cursor.fetchall()

    conn.close()
    return render_template("menu.html", opcja=opcja, menu=items)

# Składanie zamówienia
@app.route("/order", methods=["GET", "POST"])
def order():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    if session.get('user_role') != 'Klient':
        flash('Tylko klienci mogą składać zamówienia')
        return redirect(url_for('dashboard'))
    
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == "POST":
        # Pobierz dane z formularza
        pozycje = []
        for key, value in request.form.items():
            if key.startswith('pozycja_') and int(value) > 0:
                pozycja_id = int(key.split('_')[1])
                ilosc = int(value)
                pozycje.append((pozycja_id, ilosc))
        
        if not pozycje:
            flash('Musisz wybrać przynajmniej jedną pozycję')
            return redirect(url_for('order'))
        
        # Pobierz dane użytkownika (adres dostawy)
        cursor.execute("SELECT * FROM uzytkownik WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        
        # Pobierz pierwszego dostępnego dostawcę
        cursor.execute("SELECT id FROM dostawca LIMIT 1")
        dostawca = cursor.fetchone()
        
        if not dostawca:
            flash('Brak dostępnych dostawców')
            return redirect(url_for('order'))
        
        # Utwórz zamówienie
        import random
        kod_unikalny = random.randint(1000, 9999)
        
        cursor.execute("""
            INSERT INTO zamowienie (uzytkownik_id, dostawca_id, data_dostawy, 
                                  adres, miejscowosc_dostawy, kod_pocztowy_dostawy, 
                                  nr_domu_dostawy, ilosc, kod_unikalny, status)
            VALUES (%s, %s, CURDATE(), %s, %s, %s, %s, %s, %s, %s)
        """, (user_id, dostawca['id'], user['adres'], user['miejscowosc'], 
              user['kod_pocztowy'], user['nr_domu'], 1, kod_unikalny, True))
        
        zamowienie_id = cursor.lastrowid
        
        # Dodaj pozycje do zamówienia
        for pozycja_id, ilosc in pozycje:
            for _ in range(ilosc):
                cursor.execute("""
                    INSERT INTO zamowienie_pozycje (zamowienie_id, pozycja_menu_id)
                    VALUES (%s, %s)
                """, (zamowienie_id, pozycja_id))
        
        conn.commit()
        conn.close()
        
        flash(f'Zamówienie złożone pomyślnie! Kod zamówienia: {kod_unikalny}. Status: Gotowe do odbioru')
        return redirect(url_for('dashboard'))
    
    # GET - wyświetl formularz zamówienia
    # Pobierz wszystkie pozycje menu pogrupowane według opcji dietetycznych
    cursor.execute("""
        SELECT od.dieta, od.opis as dieta_opis, pm.id, pm.nazwa, pm.typ, pm.cena
        FROM pozycje_menu pm
        JOIN menu m ON pm.menu_id = m.id
        JOIN opcja_dietetyczna od ON m.opcja_dietetyczna_id = od.id
        ORDER BY od.dieta, pm.typ, pm.nazwa
    """)
    pozycje = cursor.fetchall()
    
    # Pogrupuj pozycje według diet
    menu_by_diet = {}
    for pozycja in pozycje:
        dieta = pozycja['dieta']
        if dieta not in menu_by_diet:
            menu_by_diet[dieta] = {
                'opis': pozycja['dieta_opis'],
                'pozycje': []
            }
        menu_by_diet[dieta]['pozycje'].append(pozycja)
    
    conn.close()
    return render_template("order_form.html", menu_by_diet=menu_by_diet)
# Start aplikacji
if __name__ == "__main__":
    app.run(debug=True)
