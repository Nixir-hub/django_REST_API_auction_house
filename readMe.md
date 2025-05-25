# System Aukcyjny Django REST API

## Spis treści
1. [Opis projektu](#opis-projektu)
2. [Funkcjonalności](#funkcjonalności)
3. [Modele danych](#modele-danych)
    - [Auction](#auction)
    - [Bid](#bid)
4. [Serializery](#serializery)
5. [Widoki/API Endpoints](#widokiapi-endpoints)
6. [Wymagania techniczne](#wymagania-techniczne)
7. [Instalacja](#instalacja)
8. [Użycie](#użycie)

---

## Opis projektu
System aukcyjny zbudowany na Django REST Framework, umożliwiający użytkownikom tworzenie i uczestniczenie w aukcjach online.

## Funkcjonalności
- Tworzenie i zarządzanie aukcjami
- System licytacji w czasie rzeczywistym
- Automatyczne zamykanie zakończonych aukcji (Celery)
- Pełne API REST
- System użytkowników z autentykacją

---

## Modele danych

### Auction
Reprezentuje pojedynczą aukcję.
- **owner** *(ForeignKey do User)* – właściciel aukcji
- **title** *(CharField, max_length=255)* – tytuł aukcji
- **description** *(TextField)* – opis aukcji
- **starting_price** *(DecimalField)* – cena wywoławcza
- **created_at** *(DateTimeField)* – data utworzenia
- **ends_at** *(DateTimeField)* – data zakończenia
- **highest_bid** *(DecimalField)* – aktualna najwyższa oferta
- **winner** *(ForeignKey do User, null/blank)* – zwycięzca aukcji
- **is_closed** *(BooleanField)* – status (zamknięta/otwarta)
- **status** *(property)* – zwraca 'open' lub 'closed' w zależności od zakończenia aukcji

Metody:
- **close_if_expired()** – automatycznie zamyka aukcję po upływie czasu i przypisuje zwycięzcę.
- **save()** – aktualizuje status aukcji i najwyższą ofertę.

---

### Bid
Reprezentuje ofertę w aukcji.
- **user** *(ForeignKey do User)* – użytkownik składający ofertę
- **auction** *(ForeignKey do Auction)* – powiązana aukcja
- **amount** *(DecimalField)* – kwota oferty
- **created_at** *(DateTimeField)* – data złożenia oferty

Walidacje:
- Nie można licytować po zakończeniu aukcji.
- Oferta musi być wyższa niż obecna najwyższa.
- Nie można licytować własnej aukcji.

---

## Serializery

- **AuctionSerializer** – pełna reprezentacja aukcji, zawiera historię ofert, właściciela, zwycięzcę, najwyższą ofertę, walidację daty zakończenia i ceny wywoławczej.
- **BidSerializer** – odpowiada za walidację oferty (brak licytacji własnych aukcji, kwota > najwyższa oferta, aukcja otwarta).
- **AuctionSummarySerializer** – uproszczona prezentacja aukcji (id, tytuł, cena wywoławcza, najwyższa oferta, liczba ofert, zwycięzca).
- **LoginSerializer** – dane logowania użytkownika.
- **ProfileSerializer** – dane profilowe użytkownika.
- **RegisterSerializer** – rejestracja nowego użytkownika.

---

## Widoki/API Endpoints

- **AuctionViewSet**  
  CRUD dla aukcji.  
  - GET /auctions/  
  - POST /auctions/  
  - PUT/PATCH /auctions/{id}/  
  - DELETE /auctions/{id}/  
  - GET /auctions/my-auctions/ – aukcje zalogowanego użytkownika  
  Filtrowanie aukcji po statusie (`open`, `closed`) i właścicielu (`mine=true`).

- **BidViewSet**  
  Tworzenie i podgląd ofert.  
  - GET /bids/  
  - POST /bids/  
  - GET /bids/my-bids/ – oferty zalogowanego użytkownika  
  Edycja i usuwanie ofert jest zablokowana.

- **RegisterView**  
  - POST /register/ – rejestracja użytkownika

- **LoginView, LogoutView**  
  - POST /login/ – logowanie
  - POST /logout/ – wylogowanie

- **MyProfileView**  
  - GET/PUT/DELETE /profile/ – podgląd, edycja, usuwanie profilu

- **current_user_view**  
  - GET /current-user/ – dane obecnie zalogowanego użytkownika

---

## Wymagania techniczne
- Python 3.x
- Django 5.2
- Django REST Framework
- Celery (zadania asynchroniczne)
- PostgreSQL/SQLite (baza danych)

## Instalacja
1. Sklonuj repozytorium:
    ```bash
    git clone [adres-repozytorium]
    ```
2. Utwórz i aktywuj środowisko wirtualne:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/Mac
    .\venv\Scripts\activate   # Windows
    ```
3. Zainstaluj zależności:
    ```bash
    pip install -r requirements.txt
    ```
4. Wykonaj migracje bazy danych:
    ```bash
    python manage.py migrate
    ```
5. Uruchom serwer deweloperski:
    ```bash
    python manage.py runserver
    ```

## Użycie

### Uruchomienie Celery
Aby uruchomić workera Celery:
```bash
celery -A django_REST_API_auction_house worker -l info
