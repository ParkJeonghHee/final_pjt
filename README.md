# final_pjt

Full-stack financial web app with a Django REST backend and a Vue 3 frontend.

## Overview
- Frontend: Vue 3 + Vite + Pinia + Vue Router + Bootstrap.
- Backend: Django 5 + DRF + SimpleJWT + SQLite.
- Features: product comparison (deposit/saving), metals charting, stock video search, bank map + routing, community board, user profile/portfolio.

## Project Structure
```
final_pjt/
  backend/                 # Django project
    accounts/              # Custom user + auth/profile APIs
    community/             # Posts/comments + likes
    kakao/                 # Kakao Mobility routing proxy
    metals/                # Gold/Silver time series API
    pages/                 # Health check endpoint
    products/              # Financial products + sync from external API
    data/                  # Excel files for metals series
    pjt/                   # Django settings/urls
    manage.py
    requirements.txt
  frontend/                # Vue app (Vite)
    public/                # Static data.json for map filters
    src/
      api/                 # Axios API wrappers
      assets/              # Images + data
      router/              # Vue Router config
      stores/              # Pinia stores
      views/               # Page components
      App.vue
      main.js
```

## Backend Summary
### Tech
- Django 5.2, Django REST Framework, SimpleJWT, CORS.
- SQLite (db.sqlite3).
- External data: Financial product API (FSS), Kakao Mobility, metals Excel files.

### Settings
- `backend/pjt/settings.py`:
  - `AUTH_USER_MODEL = "accounts.User"`
  - CORS allows `http://127.0.0.1:5173` and `http://localhost:5173`.
  - JWT auth headers: `Bearer`.

### Core Models
- `accounts.User`: extends `AbstractUser` with `nickname`, `age`, `total_assets`, `income`, `joined_products (M2M FinProduct)`.
- `products.FinProduct`: deposit/saving products.
- `products.FinProductOption`: interest rate options by term.
- `community.Post`, `community.Comment`: posts and comments with like relationships.

### API Endpoints (high level)
Base path: `http://127.0.0.1:8000`

Auth:
- `POST /api/token/` (JWT pair)
- `POST /api/token/refresh/`
- `POST /api/accounts/signup/`
- `GET/PATCH /api/accounts/profile/`

Products:
- `POST /api/products/sync/` (fetch from external API)
- `GET /api/products/` (filters: `type`, `bank`, `term`, `q`, `sort`)
- `GET /api/products/banks/`
- `GET /api/products/<id>/`
- `POST /api/products/<id>/join/` (JWT)

Metals:
- `GET /api/metals/series/?asset=gold|silver&start=YYYY-MM-DD&end=YYYY-MM-DD`
  - Reads `backend/data/Gold_prices.xlsx`, `backend/data/Silver_prices.xlsx`

Kakao:
- `GET /api/kakao/route/` or `/api/kakao/directions/`
  - Params: `origin`, `destination`, `priority`

Community:
- `GET /api/community/posts/?sort=latest|oldest|likes`
- `GET /api/community/posts/<id>/?sort=latest|oldest|likes`
- `POST /api/community/posts/`
- `PUT/DELETE /api/community/posts/<id>/`
- `POST /api/community/posts/<id>/like/`
- `POST /api/community/posts/<id>/comments/`
- `PUT/DELETE /api/community/comments/<id>/`
- `POST /api/community/comments/<id>/like/`

Health:
- `GET /api/pages/health/`

### External Integrations
- FSS deposit/saving products API (sync into DB).
- Kakao Mobility directions API (server proxy).

## Frontend Summary
### Tech
- Vue 3, Vite, Pinia, Vue Router, Bootstrap.
- Axios for API calls.

### Routes
```
/               Home (hero + feature cards)
/login          Login (JWT)
/signup         Signup
/profile        Profile (auth required)
/deposits       Deposit/Saving comparison table
/products/:id   Product detail + join
/metals         Gold/Silver series chart
/stocks         YouTube search for stock videos
/stocks/:id     Video detail + save
/map            Bank search + map + route
/community      Community list
/community/:id  Post detail + comments
/community/create
/community/:id/edit
```

### State/Stores
- `auth`: JWT tokens + user info in localStorage.
- `savedVideos`: saved YouTube videos in localStorage.
- `counter`: sample store (unused in UI).

### API Wrappers
- `src/api/http.js`: base axios instance with JWT header.
- `accounts.js`: profile get/update.
- `products.js`: list, banks, detail, sync.
- `metals.js`: series data.
- `community.js`: posts/comments CRUD + like toggles.
- `kakao.js`: route request to backend.
- `youtube.js`: search + video detail via YouTube API.

### Map/Data
- `public/data.json` provides region and bank lists for map filtering.
- `index.html` loads Kakao Maps SDK using `VITE_KAKAO_JS_KEY`.

## Environment Variables
Backend (`backend/.env`):
- `SECRET_KEY`
- `DEBUG`
- `ALLOWED_HOSTS`
- `FIN_API_KEY`
- `KAKAO_MOBILITY_KEY`

Frontend (`frontend/.env`):
- `VITE_KAKAO_JS_KEY` (Kakao Maps JS SDK)
- `VITE_YOUTUBE_API_KEY` (YouTube Data API)

## Local Development
Backend:
```
cd final_pjt/backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Frontend:
```
cd final_pjt/frontend
npm install
npm run dev
```

## Notes and Behaviors
- Products list auto-syncs from external API when DB is empty.
- Product detail uses JWT to show join status and to join a product.
- Metals data is from local Excel files (not live API).
- Stock videos are searched via YouTube API; video save list is localStorage-only.
- Community actions require authentication for write/like operations.
