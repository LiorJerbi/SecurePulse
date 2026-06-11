# SecurePulse
![CI](https://github.com/LiorJerbi/SecurePulse/actions/workflows/ci.yml/badge.svg)
![Coverage](https://img.shields.io/badge/coverage-86%25-brightgreen)
![Python](https://img.shields.io/badge/python-3.12-blue)

AI-powered log analysis and threat detection dashboard — a lightweight SIEM built with 
FastAPI, PostgreSQL, and React. Ingests Apache and Linux auth logs, runs 4 automated 
detection rules, and uses Gemini AI to explain each security alert in plain English. 
Includes a full pytest suite at 86% coverage with GitHub Actions CI.

![SecurePulse Dashboard](docs/Dashboard.jpg)

## Features

- **Log Ingestion** — parses Apache Combined Log Format and Linux auth.log
- **Threat Detection** — 4 automated rules: brute force SSH, HTTP scanning, privilege escalation, off-hours access
- **AI Explanations** — Gemini-powered plain-English analysis for each alert
- **REST API** — FastAPI backend with interactive docs at `/docs`
- **Dashboard** — React frontend with alerts feed, log viewer, and volume chart
- **CI/CD** — GitHub Actions runs pytest on every push

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI, Python 3.12 |
| Database | PostgreSQL 16, SQLAlchemy ORM |
| AI Layer | Google Gemini API |
| Frontend | React, Vite, Recharts |
| Infrastructure | Docker, Docker Compose |
| CI/CD | GitHub Actions |
| Testing | pytest, pytest-cov |

## Architecture

```
React Dashboard (port 5173)
        ↓ HTTP requests
FastAPI Backend (port 8000)
        ↓ SQLAlchemy ORM
PostgreSQL Database (port 5432)
        ↓ on /analyze
Detection Engine (4 rules)
        ↓ on /explain
Gemini AI API
```

## Quick Start

**Prerequisites:** Docker Desktop, Node.js 22+

```bash
# Clone the repo
git clone https://github.com/LiorJerbi/SecurePulse.git
cd SecurePulse

# Copy the example env file
On Mac/Linux: cp .env.example .env
On Windows:   copy .env.example .env
# Then edit .env and add your GEMINI_API_KEY

# Start the backend
docker-compose up --build

# Start the frontend (new terminal)
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`

## Usage

1. Upload a log file via `POST /ingest` (use `/docs` or the API directly)
2. Click **Run Analysis** on the dashboard to trigger detection
3. Click any alert to see the AI explanation

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Service health check |
| POST | `/ingest` | Upload and parse a log file |
| GET | `/logs` | Paginated log entries with filters |
| POST | `/analyze` | Run all detection rules |
| GET | `/alerts` | Retrieve alerts with filters |
| POST | `/alerts/{id}/explain` | Generate AI explanation |
| GET | `/metrics` | Detection statistics |

## Running Tests

```bash
docker exec -it securepulse-backend-1 pytest tests/ -v --cov=app --cov-report=term-missing
```

## Detection Rules

| Rule | Trigger | Severity |
|---|---|---|
| Brute Force SSH | 5+ failed SSH logins from same IP in 60s | HIGH |
| HTTP Scanner | 10+ 404 responses to same IP in 30s | MEDIUM |
| Privilege Escalation | sudo by non-whitelisted user | CRITICAL |
| Off-Hours Access | Successful login between 00:00–05:00 | MEDIUM |

## Future Work

- **Real-time log watching** — `watchdog`-based folder monitor for automatic ingestion
- **More detection rules** — port scanning, SQL injection patterns, geographic anomalies  
- **Alert deduplication** — group repeated alerts from same IP into one incident
- **Authentication** — JWT-based API auth for multi-user deployments
- **Cloud deployment** — containerized deployment on AWS ECS or Railway