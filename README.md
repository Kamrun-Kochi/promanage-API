# ProManage API

A Django REST API for project and task management with JWT authentication and Celery background tasks.

## Features

- **User Authentication**: JWT-based authentication with refresh tokens
- **Project Management**: Create, read, update, delete projects
- **Task Management**: Create, assign, and track tasks within projects
- **Background Tasks**: Email notifications via Celery
- **REST API**: Complete RESTful API endpoints

## Tech Stack

- Django 5.x
- Django REST Framework
- Simple JWT
- Celery + Redis
- PostgreSQL

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/promanage_api.git
cd promanage_api
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
```bash
cp .env.example .env
# Edit .env with your settings
```

### 5. Run migrations
```bash
python manage.py migrate
```

### 6. Start the server
```bash
python manage.py runserver
```

## Running with Celery

### Start Redis (required for Celery)
```bash
redis-server
```

### Start Celery Worker
```bash
celery -A core worker -l INFO
```

### Start Celery Beat (for scheduled tasks)
```bash
celery -A core beat -l INFO
```

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/users/register/` | Register new user |
| POST | `/api/users/token/` | Obtain JWT token |
| POST | `/api/users/token/refresh/` | Refresh JWT token |

### Projects
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/projects/` | List projects |
| POST | `/api/projects/` | Create project |
| GET | `/api/projects/{id}/` | Project detail |
| PUT | `/api/projects/{id}/` | Update project |
| DELETE | `/api/projects/{id}/` | Delete project |

### Tasks
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/projects/tasks/` | List tasks |
| POST | `/api/projects/tasks/` | Create task |
| GET | `/api/projects/tasks/{id}/` | Task detail |
| PATCH | `/api/projects/tasks/{id}/` | Update task |
| DELETE | `/api/projects/tasks/{id}/` | Delete task |

## Testing

```bash
pytest
```

## License

MIT