# Catering Project (Localhost Setup)

Projekt aplikacji cateringowej napisany w Pythonie (Flask) z frontendem w HTML/JS i backendem połączonym z bazą MySQL.

---
## Instalacja (krok po kroku)

### 1. Sklonuj repozytorium

```bash
git clone https://github.com/wiktorkwiatkowski/catering-project.git
cd catering-project
```
### Utwórz i aktywuj środowisko wirtualne
> [!WARNING]
> Upewnij się, że jesteś w katalogu `catering-project/` przed uruchomieniem komend.

```bash
python3 -m venv .venv
source .venv/bin/activate
```
Następnie w **VSC** wejdź:
1. Otwórz polecenia `Ctrl+Shift+P`
2. Wpisz `Python: Select Interpreter`
3. Wybierz interpreter z .venv (np. .venv/bin/python)

> Teraz podpowiedzi i autouzupełnianie w VSC powinno działać

#### Zainstaluj wymagane paczki
```bash
pip install -r requirements.txt
```
### 2. Konfiguracja MySQL

#### Zainstaluj MySQL (jeśli nie masz)
```bash
sudo apt update
sudo apt install mysql-server
```
> [!NOTE]
> #### Uruchom serwer MySQL
> Nie musisz tego robić, wystarczy `reboot`, potem system automatycznie będzie to robił przy starcie.
> ``` bash
> sudo systemctl start mysql
> ```
### 3. Ustaw hasło dla root 
```bash
sudo mysql
```
#### W MySQL wpisz:
``` bash
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'root';
FLUSH PRIVILEGES;
EXIT;
```
### 4. Inicjalizacja bazy danych
> W katalogu `catering-project/`
```bash
mysql -u root -p < init.sql
```
#### Wejdz do bazy danych i sprawdź czy pojawił się `catering`
```bash
mysql -u root -p 
```
> Podaj hasło `root`

Wyświetl wszystkie bazy danych:
```bash
SHOW DATABASES;
```
Wybierz `catering`
```bash
use catering
```
Wyświetl wszystko co jest w menu
```bash
SELECT * FROM menu;
```

### 5. Uruchomienie aplikacji 
```bash
python app.py
```
#### Po uruchomieniu aplikacji wejdź w przeglądarce na:
[Strona kateringu](http://localhost:5000) - localhost:5000 
