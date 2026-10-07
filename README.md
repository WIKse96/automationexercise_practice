# Automation Exercise — test framework

Framework testowy (UI + API, API w trakcie budowy) dla [automationexercise.com](https://automationexercise.com) — publicznej strony demo przeznaczonej do ćwiczenia automatyzacji testów.

**Stos:** Python, pytest, Playwright (`pytest-playwright`), `pytest-xdist` (równoległość), Allure (raportowanie), GitHub Actions (CI).

---

## Struktura projektu

```
.
├── conftest.py              # fixture'y pytest: przeglądarka, base_url, dane testowe, klient API, sprzątanie kont
├── pages/                   # Page Object Model — jedna klasa na stronę
│   ├── base_page.py         #   wspólna nawigacja/akcje (goto, nav_*, continue_button, logged_in_as...)
│   ├── login_page.py        #   /login — formularz logowania + start rejestracji
│   └── register_page.py     #   /signup — formularz Account/Address Information
├── api/
│   └── account_api.py       # klient HTTP na /api/createAccount, updateAccount, deleteAccount,
│                             #   getUserDetailByEmail, verifyLogin (Playwright APIRequestContext)
├── tests/
│   ├── ui/                  # testy sterujące przeglądarką (Playwright)
│   └── api/                 # zarezerwowane pod czyste testy HTTP bez przeglądarki — PUSTE, w trakcie
└── .github/workflows/       # CI: smoke test na każdy push do main
```

Dodatkowe `pages/`/`api/` (`home_page.py`, `products_page.py`, `cart_page.py`, `products_api.py`, `brands_api.py`, `users_api.py`) to scaffolding pod przyszłe testy katalogu produktów i koszyka — jeszcze bez pokrycia testami, nie opisuję ich dalej jako "zrobione".

---

## Podejście do testów

- **Page Object Model** — jedna klasa na stronę, lokatory jako `@property`, testy wołają metody, nie selektory.
- **Konfigurowalne środowisko** — domena czytana z `.env` (`base_url`), nie zahardkodowana; zmiana na staging to jedna zmienna.
- **Asercje niezależne od locale przeglądarki** — walidacja formularza sprawdzana przez `:invalid` (CSS), nie przez tekst natywnego komunikatu, bo ten zależy od języka.
- **Dokumentowanie realnych bugów** — znalezione błędy strony nie są ignorowane; test zostaje z `@pytest.mark.xfail(strict=True)` i pełnym opisem w Allure (tag, severity, oczekiwane vs faktyczne, screenshot). `strict=True` sprawia, że naprawa buga na stronie automatycznie zgłasza się jako failing test, do zaktualizowania.
- **Allure jako warstwa raportowa** — `feature`/`story`/`step` na każdym teście, automatyczny screenshot przy niepowodzeniu (hook w `conftest.py`).
- **Sprzątanie danych zawsze** — konta zakładane w testach są rejestrowane do usunięcia *przed* wykonaniem akcji i kasowane przez API w teardownie, niezależnie od wyniku testu.

---

## Co jest przetestowane (UI)

| Plik | Zakres |
|---|---|
| `test_register_e2e.py` | Smoke: pełna ścieżka do formularza rejestracji, obecność wszystkich pól i opcji kraju (oznaczony `@pytest.mark.smoke` — to jedyny test uruchamiany w CI) |
| `test_signup_labels.py` | Powiązanie `<label for="...">` z właściwym polem dla wszystkich 16 pól formularza — dostępność (a11y) |
| `test_signup_country.py` | Wybór każdego z 7 krajów + weryfikacja przez API i w adresie dostawy na checkout; domyślna wartość i kolejność opcji |
| `test_signup_boundary.py` | Walidacja formularza: puste wymagane pola blokują submit, same pola opcjonalne nie wystarczą, dowolna krótka wartość satysfakcjonuje `required` (brak `pattern`/`minlength`), brak limitu długości (255/256 znaków) na żadnym polu tekstowym |

## API — w trakcie

`api/account_api.py` już istnieje i jest używany **wewnątrz testów UI** do zakładania/weryfikowania/kasowania kont przez HTTP (Playwright `APIRequestContext`, nie `requests`). `tests/api/` — katalog na czyste testy samego API, bez przeglądarki — jest na razie pusty; to następny etap.

---

## Uruchamianie

```bash
pip install -r requirements.txt
playwright install chromium

cp .env.example .env     # i ewentualnie zmień BASE_URL na inne środowisko

pytest                              # cały zestaw
pytest -m smoke                     # tylko smoke
pytest -n 4                         # równolegle (bezpieczna liczba workerów dla tej strony)
pytest --headed                     # z widoczną przeglądarką
```

### Raport Allure

```bash
pytest --alluredir=reports/allure_results
allure serve reports/allure_results
```

### CI

GitHub Actions (`.github/workflows/tests.yml`) odpala `pytest -m smoke` na każdy push do `main` — świeża maszyna, instalacja zależności + Chromium od zera, raport zapisany jako artefakt niezależnie od wyniku.
