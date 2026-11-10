# MoyoCare

**An Offline-First Community Health Reporting and Surveillance Platform**

MoyoCare is a community health reporting platform designed to support Health Surveillance Assistants (HSAs) in capturing, managing and reporting community-level health information in Malawi.

The platform aims to improve the timeliness, consistency and accessibility of community health data by providing a structured digital reporting workflow that works in environments with limited or unreliable internet connectivity.

MoyoCare enables health workers to record patient encounters, document reported symptoms and actions taken, and securely synchronize records with a centralized backend for supervisory review and public health monitoring.

## Core Objectives

- Digitize community-level health encounter reporting.
- Support reliable data collection in areas with limited connectivity.
- Improve the visibility and traceability of community health reports.
- Enable supervisors to monitor reported cases and identify potential disease trends.
- Reduce duplicate, incomplete and inconsistent reporting.
- Establish a foundation for data-driven community health interventions.

## System Architecture

MoyoCare follows an offline-first, client-server architecture.

The Android application is designed to support local data persistence and deferred synchronization, while the backend provides centralized data management, authentication, validation and reporting capabilities.

**Primary components:**

- **Mobile application:** Android application developed using Kotlin.
- **Backend API:** Django and Django REST Framework.
- **Database:** PostgreSQL.
- **Authentication:** JSON Web Token (JWT).
- **API documentation:** OpenAPI documentation using drf-spectacular.
- **Synchronization:** Designed for reliable submission and synchronization of locally stored records.

## Technology Stack

| Component                  | Technology                         |
| -------------------------- | ---------------------------------- |
| Backend                    | Python, Django 5.2                 |
| API                        | Django REST Framework              |
| Database                   | PostgreSQL                         |
| Authentication             | SimpleJWT                          |
| API Documentation          | drf-spectacular                    |
| Filtering                  | django-filter                      |
| Android                    | Kotlin                             |
| Local Persistence          | Room                               |
| Background Synchronization | WorkManager                        |
| HTTP Client                | Retrofit / OkHttp                  |
| Testing                    | pytest, pytest-django, factory-boy |
| Code Quality               | Ruff                               |
| Deployment                 | Docker, Gunicorn                   |

## Core Functional Areas

### Community Health Reporting

- Capture patient encounters and reported symptoms.
- Record relevant demographic information.
- Document actions taken, including treatment and referrals.
- Associate reports with their respective health facilities and communities.

### Offline Data Collection

- Support local storage of reports on Android devices.
- Allow health workers to submit reports without an active internet connection.
- Synchronize pending records when connectivity becomes available.
- Maintain reliable submission handling across network interruptions.

### Data Synchronization

- Support client-generated unique identifiers for submitted records.
- Prevent duplicate reports through server-side idempotency controls.
- Track client recording timestamps and server receipt timestamps.
- Provide a foundation for synchronization error handling and retry mechanisms.

### Supervisory Monitoring

- Provide centralized access to submitted community health reports.
- Support filtering by reporting date, village, facility and reported symptoms.
- Enable monitoring of case patterns and potential disease clusters.
- Provide a foundation for operational and public health reporting dashboards.

### Security and Access Control

- JWT-based authentication.
- Role-based authorization.
- Facility-scoped data access.
- Input validation and controlled data exposure.
- Auditability of relevant user and reporting activities.

MoyoCare is intended for reporting and public health monitoring. It is not a diagnostic system and does not replace professional clinical assessment.

## Backend Architecture

The backend is organized as a modular Django application, with domain-oriented applications responsible for distinct areas of the system.

```text
backend/
├── src/
│   ├── config/
│   │   └── settings/
│   ├── apps/
│   │   ├── accounts/
│   │   ├── organizations/
│   │   ├── facilities/
│   │   ├── patients/
│   │   ├── reporting/
│   │   ├── synchronization/
│   │   └── audit/
│   └── common/
├── tests/
├── pyproject.toml
├── Dockerfile
└── .env.example

mobile/
infrastructure/
docs/
```

The architecture follows a modular monolith approach, keeping domain responsibilities separated while maintaining a single deployable backend.

## API

The backend exposes a versioned REST API.

Base path:

```text
/api/v1/
```

API documentation is provided through OpenAPI, allowing developers to inspect available endpoints, request schemas and response formats.

## Development Setup

### Prerequisites

- Python 3.12+
- PostgreSQL
- Git
- Docker and Docker Compose (recommended)

### Clone the repository

```bash
git clone https://github.com/ChifundoGKauwa/moyocare.git
cd moyocare
```

### Configure the backend

```bash
cd backend

python3 -m venv .venv
source .venv/bin/activate

pip install -e ".[dev]"
```

### Environment configuration

Create a local environment file using the example configuration:

```bash
cp .env.example .env
```

Configure the required application and database environment variables before starting the backend.

Never commit production credentials, secret keys or sensitive configuration values to version control.

### Run database migrations

After configuring PostgreSQL and the application settings:

```bash
python src/manage.py makemigrations
python src/manage.py migrate
```

### Start the development server

```bash
python src/manage.py runserver
```

## Testing

Run the automated test suite:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=src --cov-report=term-missing
```

Run static analysis:

```bash
ruff check .
```

## Security and Data Protection

MoyoCare is designed to handle sensitive community health information. Security and privacy are therefore core architectural considerations.
