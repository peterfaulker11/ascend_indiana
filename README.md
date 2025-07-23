## ⚙️ Setup Instructions - macOS only

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/skills-api.git
cd skills-api
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Install and configure Postgres
```bash
brew install postgresql
brew services start postgresql
```
```bash
psql postgres
```
```bash
CREATE ROLE postgres WITH LOGIN PASSWORD 'postgres';
ALTER ROLE postgres CREATEDB;
CREATE DATABASE skills_db OWNER postgres;
\q
```

### 5. Run database migrations
```bash
python manage.py migrate
```

### 6. Create a superuser
```bash
python manage.py createsuperuser
```

### 7. Start the development server
```bash
python manage.py runserver
```

### 8. Run tests
```bash
python manage.py test
```

API Endpoints

    GET /api/skills/ – List all skills

    GET /api/skills/<slug>/ – Get skill by slug

    GET /api/skills/recommend/?category=<slug>&user_id=<id> – Recommend skills for a user

    POST /api/user-skills/ – Record that a user learned a skill

Example POST body for /api/user-skills/:
```bash
{
  "user_id": 42,
  "skill": 1,
  "proficiency": 4,
  "learned_at": "2025-01-01"
}
```






