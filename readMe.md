# System Aukcyjny Django REST API
## Opis Projektu
System aukcyjny zbudowany przy użyciu Django REST Framework, umożliwiający użytkownikom tworzenie i uczestniczenie w aukcjach online.
## Funkcjonalności
- Tworzenie i zarządzanie aukcjami
- System licytacji w czasie rzeczywistym
- Automatyczne zamykanie zakończonych aukcji (wykorzystanie Celery)
- Pełne API REST
- System użytkowników z autentykacją

## Modele Danych
### Auction (Aukcja)
- Tytuł
- Opis
- Cena wywoławcza
- Data utworzenia
- Data zakończenia
- Najwyższa oferta
- Status (otwarta/zamknięta)
- Właściciel
- Zwycięzca aukcji

### Bid (Oferta)
- Kwota
- Data złożenia
- Powiązanie z aukcją
- Powiązanie z użytkownikiem

## Wymagania Techniczne
- Python 3.x
- Django 5.2
- Django REST Framework
- Celery (do zadań asynchronicznych)
- PostgreSQL/SQLite (baza danych)

## Instalacja
1. Sklonuj repozytorium:
``` bash
git clone [adres-repozytorium]
```
1. Utwórz i aktywuj środowisko wirtualne:
``` bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
```
1. Zainstaluj zależności:
``` bash
pip install -r requirements.txt
```
1. Wykonaj migracje bazy danych:
``` bash
python manage.py migrate
```
1. Uruchom serwer deweloperski:
``` bash
python manage.py runserver
```
## Użycie
### Uruchomienie Celery
Aby uruchomić workera Celery:
``` bash
celery -A django_REST_API_auction_house worker -l info
```
Aby uruchomić harmonogram zadań Celery:
``` bash
celery -A django_REST_API_auction_house beat -l info
```
