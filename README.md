# RoomLoop Database Foundation

## MySQL Prerequisites

- MySQL Community Server 8.x or a compatible MySQL 8 server
- MySQL client tools or MySQL Workbench to run the SQL scripts

## Database Creation

Create the `roomloop` database before running the SQL scripts. The schema script creates it if it does not already exist, so `DATABASE_NAME` should be set to `roomloop`.

## Execute `schema.sql`

Run the schema initialization script to create the `rooms`, `recurring_series`, and `bookings` tables:

```bash
mysql -h "$DATABASE_HOST" -P "$DATABASE_PORT" -u "$DATABASE_USER" -p < database/schema.sql
```

## Execute `seed.sql`

After the schema is created, load the seed data:

```bash
mysql -h "$DATABASE_HOST" -P "$DATABASE_PORT" -u "$DATABASE_USER" -p "$DATABASE_NAME" < database/seed.sql
```

## Required Environment Variables

Set the following environment variables for the MySQL connection used by the application:

- `DATABASE_HOST`
- `DATABASE_PORT`
- `DATABASE_NAME`
- `DATABASE_USER`
- `DATABASE_PASSWORD`
# RoomLoop

RoomLoop is a backend meeting room booking system built using **FastAPI**, **SQLAlchemy**, and **MySQL**.

The implementation supports:

- Single room bookings
- Weekly recurring bookings
- Booking conflict detection
- Recurring booking cancellation
- Timezone-aware scheduling
- Daylight Saving Time (DST) handling
- Layered architecture (API → Service → Repository → Database)
- Comprehensive automated testing

---

# Prerequisites

Ensure the following software is installed before running the project:

- Python 3.12 or later
- MySQL 8.x
- Make
- Git

---

# Project Setup

Clone the repository and move to the project root.

```bash
git clone <repository-url>
cd RoomLoop
```

Run the initial setup:

```bash
make setup
```

This command:

- Creates a Python virtual environment
- Installs all project dependencies

---

# Environment Configuration

Create a `.env` file using `.env.example` as the reference.

Populate the required values:

```
APP_NAME
APP_ENV
HOST
PORT
DATABASE_HOST
DATABASE_PORT
DATABASE_NAME
DATABASE_USER
DATABASE_PASSWORD
TIMEZONE_DEFAULT
```

---

# Database Setup

Initialize the database with:

```bash
make db-init
```

This command automatically:

- Creates the `roomloop` database (if required)
- Executes `database/schema.sql`
- Loads `database/seed.sql`

---

# Running the Application

Start the FastAPI application:

```bash
make run
```

The API will be available at:

```
http://localhost:<PORT>
```

Swagger UI:

```
http://localhost:<PORT>/docs
```

OpenAPI Specification:

```
http://localhost:<PORT>/openapi.json
```

---

# Running the Test Suite

Execute the complete automated test suite:

```bash
make test
```

The test suite validates:

- Configuration
- Database
- SQLAlchemy Models
- Repository Layer
- Pydantic Schemas
- Service Layer
- API Layer
- Integration Workflows
- Submission Readiness

---

# Available Make Commands

| Command | Description |
|---------|-------------|
| `make setup` | Create virtual environment and install dependencies |
| `make db-init` | Create database, schema and seed data |
| `make run` | Start the FastAPI application |
| `make test` | Execute the complete automated test suite |
| `make clean` | Remove generated caches and temporary files |

---

# Project Documentation

The project documentation is organized as follows:

| Document | Purpose |
|----------|---------|
| `docs/requirements.md` | Assignment requirements analysis |
| `docs/TSD.md` | Technical Solution Document describing the overall design |
| `docs/DECISIONS.md` | Engineering decisions and ambiguity resolution |
| `docs/AI_ASSISTED_DEVELOPMENT.md` | AI-assisted development workflow, validation process and refinements |
| `docs/execution_roadmap.md` | Milestone-wise implementation roadmap |
| `docs/backend_agent_checklist.md` | Backend implementation checklist |
| `docs/testing_agent_checklist.md` | Testing strategy and checklist |

It is recommended to read the documents in the following order:

1. `docs/requirements.md`
2. `docs/TSD.md`
3. `docs/DECISIONS.md`
4. `docs/AI_ASSISTED_DEVELOPMENT.md`

---

# Project Structure

```
app/
    api/
    core/
    database/
    models/
    repositories/
    schemas/
    services/

database/
docs/
tests/
run.py
Makefile
README.md
```

---

# Notes

- The implementation preserves the existing API route naming convention to maintain backward compatibility.
- Timezone and DST handling follow the design documented in the Technical Solution Document.
- All engineering decisions and requirement ambiguities are documented in `docs/DECISIONS.md`.
- The project was developed using an AI-assisted engineering workflow with manual validation of all architectural decisions.