# Student Assessment Platform

A web-based assessment platform for computer science students, built with **FastAPI**, **SQLAlchemy**, **PostgreSQL**, and **JavaScript**.

The project covers the full assessment workflow: authentication, role-based access, test sessions, question management, result processing, statistics, and administration.

## Highlights

- asynchronous Python backend built with FastAPI
- PostgreSQL persistence with SQLAlchemy and `asyncpg`
- role-based access for students, teachers, and administrators
- JWT-based authentication with server-side session tracking
- student testing workflows and timed test sessions
- automated answer checking and result processing
- student performance statistics and analytics
- teacher tools for question and assessment management
- administrator tools for user and database management
- server-rendered HTML with JavaScript-enhanced interfaces

## Tech Stack

### Backend

- Python
- FastAPI
- SQLAlchemy
- asyncpg
- aiofiles

### Database

- PostgreSQL

### Authentication & Security

- JWT
- Passlib
- HTTP-only cookies
- role-based authorization
- server-side user sessions

### Frontend

- JavaScript
- HTML / Jinja templates
- CSS

## Architecture

The application is split into dedicated modules for endpoints, database access, business logic, models, and shared types.

```text
.
├── main.py
├── modules/
│   ├── _types/
│   ├── databases/
│   ├── endpoints/
│   │   ├── static/
│   │   └── templates/
│   ├── errors/
│   ├── functions/
│   └── models/
├── requirements.txt
└── database.csv
```

### Main application flow

```text
Browser / JavaScript UI
        │
        ▼
     FastAPI
        │
        ├── authentication & roles
        ├── assessment workflows
        ├── statistics
        └── administration
        │
        ▼
 SQLAlchemy / asyncpg
        │
        ▼
    PostgreSQL
```

## Roles

The application implements separate access levels for:

- **Student** — takes assessments and reviews personal statistics
- **Teacher** — works with questions, tests, and student statistics
- **Administrator** — manages users and database-related operations

Authorization is enforced in backend dependencies rather than only in the UI.

## Assessment Workflow

The platform supports:

- starting and tracking active test sessions
- loading assessment variants and individual tasks
- saving answers during a session
- checking answers
- processing test results
- storing user statistics
- calculating accuracy and performance metrics
- collecting daily statistics

The system contains assessment logic for computer science exam topics and can track performance across multiple problem categories.

## Authentication

Authentication uses JWT access tokens stored in HTTP-only cookies together with server-side session records.

Protected routes validate both the authenticated user and the required application role before granting access.

## Database Layer

The project uses multiple database-oriented modules for:

- users
- user sessions
- active student tests
- student statistics
- daily statistics
- informatics questions and assessment data
- database history / archive operations

Database operations are designed around asynchronous PostgreSQL access.

## Local Setup

### Requirements

- Python 3.10+
- PostgreSQL

Clone the repository:

```bash
git clone https://github.com/dAspergillusb/egeTests.git
cd egeTests
```

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows:

```powershell
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

The application reads PostgreSQL and authentication settings from `.env`. If `.env` is not present, the current configuration code can generate an initial configuration interactively.

Start the application with an ASGI server, for example:

```bash
uvicorn main:MAIN --reload
```

## Configuration

The application supports configuration for:

- PostgreSQL host and port
- database user and password
- application database names
- JWT secret key and algorithm
- access-token lifetime

The `.env` file is excluded from Git and should be used for local or deployment-specific secrets.

## Project Context

This project was developed as a practical educational platform for computer science assessment. It represents an end-to-end development effort covering backend architecture, database design, authentication, application logic, frontend integration, testing workflows, and deployment-oriented configuration.

## Author

**Nikita Zelentsov**  
Python Backend Developer

GitHub: [@dAspergillusb](https://github.com/dAspergillusb)
