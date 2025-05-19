DROP DATABASE IF EXISTS catering;
CREATE DATABASE catering;
USE catering;

-- Tabela użytkowników
CREATE TABLE uzytkownicy (
    id INT AUTO_INCREMENT PRIMARY KEY,
    imie VARCHAR(100),
    nazwisko VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    haslo VARCHAR(255) NOT NULL
);

-- Tabela ról
CREATE TABLE role (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nazwa VARCHAR(50) NOT NULL UNIQUE
);

-- Tabela relacji użytkownik <-> rola (wiele do wielu)
CREATE TABLE uzytkownicy_role (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uzytkownik_id INT,
    rola_id INT,
    FOREIGN KEY (uzytkownik_id) REFERENCES uzytkownicy(id) ON DELETE CASCADE,
    FOREIGN KEY (rola_id) REFERENCES role(id) ON DELETE CASCADE
);

-- Menu na dany dzień
CREATE TABLE menu (
    id INT AUTO_INCREMENT PRIMARY KEY,
    data DATE NOT NULL,
    opis TEXT
);

-- Konkretne pozycje menu (śniadanie, obiad, kolacja itd.)
CREATE TABLE pozycje_menu (
    id INT AUTO_INCREMENT PRIMARY KEY,
    menu_id INT,
    nazwa VARCHAR(100),
    typ ENUM('sniadanie', 'obiad', 'kolacja') NOT NULL,
    cena DECIMAL(6,2) NOT NULL,
    FOREIGN KEY (menu_id) REFERENCES menu(id) ON DELETE CASCADE
);

-- Zamówienia składane przez klientów
CREATE TABLE zamowienia (
    id INT AUTO_INCREMENT PRIMARY KEY,
    klient_id INT,
    dostawca_id INT,
    data_realizacji DATE NOT NULL,
    liczba_zestawow INT,
    preferencje_dietetyczne TEXT,
    FOREIGN KEY (klient_id) REFERENCES uzytkownicy(id),
    FOREIGN KEY (dostawca_id) REFERENCES uzytkownicy(id)
);

-- Pozycje przypisane do zamówień
CREATE TABLE zamowienia_pozycje (
    id INT AUTO_INCREMENT PRIMARY KEY,
    zamowienie_id INT,
    pozycja_menu_id INT,
    FOREIGN KEY (zamowienie_id) REFERENCES zamowienia(id) ON DELETE CASCADE,
    FOREIGN KEY (pozycja_menu_id) REFERENCES pozycje_menu(id) ON DELETE CASCADE
);

-- Oceny wystawiane po dostawie
CREATE TABLE oceny (
    id INT AUTO_INCREMENT PRIMARY KEY,
    zamowienie_id INT UNIQUE,
    klient_id INT,
    dostawca_id INT,
    ocena INT CHECK (ocena BETWEEN 0 AND 5),
    komentarz TEXT,
    FOREIGN KEY (zamowienie_id) REFERENCES zamowienia(id) ON DELETE CASCADE,
    FOREIGN KEY (klient_id) REFERENCES uzytkownicy(id),
    FOREIGN KEY (dostawca_id) REFERENCES uzytkownicy(id)
);

-- Wstawienie przykładowych ról
INSERT INTO role (nazwa) VALUES ('klient'), ('administrator'), ('dostawca');


-- Przykładowi użytkownicy
INSERT INTO uzytkownicy (imie, nazwisko, email, haslo) VALUES
('Jan', 'Kowalski', 'jan.kowalski@example.com', 'tajne1'),
('Anna', 'Nowak', 'anna.nowak@example.com', 'tajne2'),
('Piotr', 'Zielinski', 'piotr.zielinski@example.com', 'tajne3');

-- Przypisanie ról
-- Jan to klient (id=1), Anna to dostawca (id=3), Piotr to administrator (id=2)
INSERT INTO uzytkownicy_role (uzytkownik_id, rola_id) VALUES
(1, 1), -- Jan -> klient
(2, 3), -- Anna -> dostawca
(3, 2); -- Piotr -> administrator

-- Przykładowe menu
INSERT INTO menu (data, opis) VALUES
('2025-05-20', 'Menu na wtorek: fit'),
('2025-05-21', 'Menu na środę: klasyczne');

-- Przykładowe pozycje w menu
INSERT INTO pozycje_menu (menu_id, nazwa, typ, cena) VALUES
(1, 'Jajecznica z warzywami', 'sniadanie', 12.50),
(1, 'Kurczak z ryżem', 'obiad', 22.00),
(1, 'Sałatka grecka', 'kolacja', 15.00),
(2, 'Owsianka z owocami', 'sniadanie', 11.00),
(2, 'Spaghetti bolognese', 'obiad', 21.00),
(2, 'Kanapka z hummusem', 'kolacja', 13.00);

-- Przykładowe zamówienie
INSERT INTO zamowienia (klient_id, dostawca_id, data_realizacji, liczba_zestawow, preferencje_dietetyczne) VALUES
(1, 2, '2025-05-20', 2, 'bez laktozy');

-- Przypisanie pozycji do zamówienia
INSERT INTO zamowienia_pozycje (zamowienie_id, pozycja_menu_id) VALUES
(1, 1), (1, 2), (1, 3);

-- Ocena za zamówienie
INSERT INTO oceny (zamowienie_id, klient_id, dostawca_id, ocena, komentarz) VALUES
(1, 1, 2, 5, 'Wszystko smaczne i na czas!');