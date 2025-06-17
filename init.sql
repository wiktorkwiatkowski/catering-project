DROP DATABASE IF EXISTS catering;
CREATE DATABASE catering;
USE catering;
DROP TABLE IF EXISTS ocena;
DROP TABLE IF EXISTS zamowienie_pozycje;
DROP TABLE IF EXISTS zamowienie;
DROP TABLE IF EXISTS pozycje_menu;
DROP TABLE IF EXISTS menu;
DROP TABLE IF EXISTS dostawca;
DROP TABLE IF EXISTS administrator;
DROP TABLE IF EXISTS opcja_dietetyczna;
DROP TABLE IF EXISTS uzytkownik;

-- Tabela uzytkownik z rola ENUM
CREATE TABLE uzytkownik (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rola ENUM('Klient', 'Dostawca', 'Administrator') NOT NULL,
    imie VARCHAR(32),
    nazwisko VARCHAR(32),
    email VARCHAR(50) UNIQUE NOT NULL,
    haslo VARCHAR(255) NOT NULL,
    numer_telefonu VARCHAR(15),
    adres VARCHAR(255)
);

-- Tabela administrator (FK do uzytkownik)
CREATE TABLE administrator (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uzytkownik_id INT UNIQUE,
    FOREIGN KEY (uzytkownik_id) REFERENCES uzytkownik(id) ON DELETE CASCADE
);

-- Tabela dostawca (FK do uzytkownik)
CREATE TABLE dostawca (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uzytkownik_id INT UNIQUE,
    FOREIGN KEY (uzytkownik_id) REFERENCES uzytkownik(id) ON DELETE CASCADE
);

-- Tabela opcja dietetyczna
CREATE TABLE opcja_dietetyczna (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dieta ENUM('Standard', 'Weganska', 'Niskoweglowa', 'Vegetarianska', 'Sport', 'Bez laktozy') NOT NULL,
    opis VARCHAR(255)
);

-- Tabela menu
CREATE TABLE menu (
    id INT AUTO_INCREMENT PRIMARY KEY,
    opcja_dietetyczna_id INT,
    data_dostepnosci DATE NOT NULL,
    cena FLOAT,
    opis VARCHAR(255),
    FOREIGN KEY (opcja_dietetyczna_id) REFERENCES opcja_dietetyczna(id) ON DELETE SET NULL
);

-- Tabela pozycje_menu (zawiera pozycje z menu)
CREATE TABLE pozycje_menu (
    id INT AUTO_INCREMENT PRIMARY KEY,
    menu_id INT,
    nazwa VARCHAR(100),
    typ ENUM('sniadanie', 'obiad', 'kolacja') NOT NULL,
    cena DECIMAL(6,2) NOT NULL,
    FOREIGN KEY (menu_id) REFERENCES menu(id) ON DELETE CASCADE
);

-- Tabela zamowienie
CREATE TABLE zamowienie (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uzytkownik_id INT,
    menu_id INT,
    dostawca_id INT,
    data_dostawy DATE NOT NULL,
    adres VARCHAR(50),
    ilosc INT,
    kod_unikalny INT(4),
    status BOOLEAN,
    opcja_dietetyczna_id INT,
    FOREIGN KEY (uzytkownik_id) REFERENCES uzytkownik(id),
    FOREIGN KEY (menu_id) REFERENCES menu(id),
    FOREIGN KEY (dostawca_id) REFERENCES dostawca(id),
    FOREIGN KEY (opcja_dietetyczna_id) REFERENCES opcja_dietetyczna(id)
);

-- Tabela zamowienie_pozycje (zawiera pozycje z menu przypisane do zamowienia)
CREATE TABLE zamowienie_pozycje (
    id INT AUTO_INCREMENT PRIMARY KEY,
    zamowienie_id INT,
    pozycja_menu_id INT,
    FOREIGN KEY (zamowienie_id) REFERENCES zamowienie(id) ON DELETE CASCADE,
    FOREIGN KEY (pozycja_menu_id) REFERENCES pozycje_menu(id) ON DELETE CASCADE
);

-- Tabela ocena (ocena dotyczy konkretnego zamowienia)
CREATE TABLE ocena (
    id INT AUTO_INCREMENT PRIMARY KEY,
    zamowienie_id INT UNIQUE,
    liczba_gwiazdek INT CHECK (liczba_gwiazdek BETWEEN 0 AND 5),
    FOREIGN KEY (zamowienie_id) REFERENCES zamowienie(id) ON DELETE CASCADE
);

-- -------------------------------------------------
-- PRZYKLADOWE DANE
-- -------------------------------------------------

-- Uzytkownicy
INSERT INTO uzytkownik (rola, imie, nazwisko, email, haslo, numer_telefonu, adres) VALUES
('Klient', 'Jan', 'Kowalski', 'jan.kowalski@example.com', 'haslo123', '123456789', 'ul. Kwiatowa 5'),
('Dostawca', 'Anna', 'Nowak', 'anna.nowak@example.com', 'haslo456', '987654321', 'ul. Ogrodowa 10'),
('Administrator', 'Piotr', 'Zielinski', 'piotr.zielinski@example.com', 'haslo789', '555666777', 'ul. Polna 3');

-- Administrator FK
INSERT INTO administrator (uzytkownik_id) VALUES (3);

-- Dostawca FK
INSERT INTO dostawca (uzytkownik_id) VALUES (2);

-- Opcje dietetyczne
INSERT INTO opcja_dietetyczna (dieta, opis) VALUES
('Standard', 'Standardowa dieta dla każdego'),
('Weganska', 'Bez produktów odzwierzęcych'),
('Niskoweglowa', 'Niska zawartość węglowodanów'),
('Vegetarianska', 'Bez mięsa, produkty roślinne'),
('Sport', 'Dieta dla osób aktywnych fizycznie'),
('Bez laktozy', 'Bez laktozy dla osób nietolerujących');

-- Menu
INSERT INTO menu (opcja_dietetyczna_id, data_dostepnosci, cena, opis) VALUES
(1, '2025-05-20', 50.00, 'Menu na wtorek: fit'),
(2, '2025-05-21', 55.00, 'Menu na środę: klasyczne');

-- Pozycje menu
INSERT INTO pozycje_menu (menu_id, nazwa, typ, cena) VALUES
(1, 'Jajecznica z warzywami', 'sniadanie', 12.50),
(1, 'Kurczak z ryżem', 'obiad', 22.00),
(1, 'Sałatka grecka', 'kolacja', 15.00),
(2, 'Owsianka z owocami', 'sniadanie', 11.00),
(2, 'Spaghetti bolognese', 'obiad', 21.00),
(2, 'Kanapka z hummusem', 'kolacja', 13.00);

-- Zamowienie
INSERT INTO zamowienie (uzytkownik_id, menu_id, dostawca_id, data_dostawy, adres, ilosc, kod_unikalny, status, opcja_dietetyczna_id) VALUES
(1, 1, 1, '2025-05-20', 'ul. Kwiatowa 5', 2, 1234, TRUE, 6);

-- Zamowienie_pozycje
INSERT INTO zamowienie_pozycje (zamowienie_id, pozycja_menu_id) VALUES
(1, 1), (1, 2), (1, 3);

-- Ocena
INSERT INTO ocena (zamowienie_id, liczba_gwiazdek) VALUES
(1, 5);

USE catering;

-- Dodaj nowe kolumny do tabeli uzytkownik
ALTER TABLE uzytkownik 
ADD COLUMN miejscowosc VARCHAR(100) AFTER adres,
ADD COLUMN kod_pocztowy VARCHAR(10) AFTER miejscowosc,
ADD COLUMN nr_domu VARCHAR(20) AFTER kod_pocztowy;

-- Dodaj nowe kolumny do tabeli zamowienie (jeśli potrzebujesz szczegółowego adresu dostawy)
ALTER TABLE zamowienie 
ADD COLUMN miejscowosc_dostawy VARCHAR(100) AFTER adres,
ADD COLUMN kod_pocztowy_dostawy VARCHAR(10) AFTER miejscowosc_dostawy,
ADD COLUMN nr_domu_dostawy VARCHAR(20) AFTER kod_pocztowy_dostawy;

-- Opcjonalnie: możesz usunąć stare kolumny adres po przeniesieniu danych
-- ALTER TABLE uzytkownik DROP COLUMN adres;
-- ALTER TABLE zamowienie DROP COLUMN adres;

-- Aktualizacja przykładowych danych
UPDATE uzytkownik SET 
    miejscowosc = 'Wrocław',
    kod_pocztowy = '50-001',
    nr_domu = '5'
WHERE email = 'jan.kowalski@example.com';

UPDATE uzytkownik SET 
    miejscowosc = 'Kraków',
    kod_pocztowy = '30-001',
    nr_domu = '10'
WHERE email = 'anna.nowak@example.com';

UPDATE uzytkownik SET 
    miejscowosc = 'Warszawa',
    kod_pocztowy = '00-001',
    nr_domu = '3'
WHERE email = 'piotr.zielinski@example.com';