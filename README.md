# Issue Tracker API

## Overview

The Issue Tracker API is a backend service built using FastAPI and PostgreSQL.
It allows users to manage issues, comments, and labels, and includes advanced
features such as optimistic concurrency control, transactional bulk updates,
CSV imports, reporting, and an audit timeline.

This project was developed as a backend assignment focusing on real-world
engineering challenges such as data integrity, validation, concurrency handling,
and database transactions.

---

## Tech Stack

- Python 3.11+
- FastAPI
- PostgreSQL
- SQLAlchemy ORM
- Pydantic
- Uvicorn

---

## Features

- User management
- Issue CRUD operations with version-based optimistic locking
- Issue listing with filters, sorting, and pagination
- Comment management with validation, pagination and filters
- Label management (many-to-many relationship with issues)
- Transactional bulk issue status updates with rollback on failure
- CSV import for issue creation with row-level validation and summary report
- Reports:
  - Top assignees
  - Average issue resolution time
- Issue timeline (audit trail of issue changes)

---

## Project Structure

```text
app/
├── main.py
├── database.py
├── models/
│   ├── __init__.py
│   ├── comment.py
│   ├── issue_event.py
│   ├── issue_label.py
│   ├── issue.py
│   ├── label.py
│   ├── user.py
├── routers/
│   ├── comments.py
│   ├── issues.py
│   ├── labels.py
│   ├── reports.py
│   ├── users.py
├── schemas/
│   ├── comment.py
│   ├── issue.py
│   ├── label.py
│   ├── report.py
│   ├── user.py
├── utils/
│   ├── security.py
│   ├── timeline.py

.env.example
requirements.txt
README.md
TEST_CASES.md
CSV Format.txt
Sample Data Flow.csv
```

---

## Setup Instructions

### Prerequisites

- Python 3.11 or higher
- PostgreSQL installed and running (running locally or remotely)

### Installation Steps

1. Clone the repository
2. Create and activate a virtual environment
3. Install dependencies
4. Configure environment variables
5. Run the application

### Install Dependencies

pip install -r requirements.txt

---

## Environment Variables

Create a .env file using the .env.example file as reference.

Required variable:

- DATABASE_URL=postgresql://<username>:<password>@localhost:5432/issue_tracker

---

## Running the Application

uvicorn app.main:app --reload

Swagger UI:
http://127.0.0.1:8000/docs

APIs can also be tested using Postman by sending requests to:
http://127.0.0.1:8000

---

## API Testing

All API endpoints were tested using:
- Swagger UI
- Postman

Detailed test cases and expected outcomes are documented in **TEST_CASES.md**.

---

## CSV Import

POST /issues/import-csv

- Accepts CSV file upload
- Validates each row independently
- Creates valid issues
- Skips invalid rows
- Returns a summary report

CSV format is documented in **CSV Format.txt**.
A sample file is provided as **Sample Data Flow.csv**.

---

## Reports

Available report endpoints:

- GET /reports/top-assignees
- GET /reports/average-latency

Reports use database-level aggregation for performance and accuracy.

---

## Issue Timeline (Bonus Feature)

Endpoint: 

- GET /issues/{issue_id}/timeline

Provides a chronological audit trail of issue events such as:

- Issue creation
- Status changes
- Priority changes
- Comments added
- Label updates

Timeline events are stored as append-only logs.

---

## Submission Checklist

- [x] Application runs locally without errors
- [x] PostgreSQL database configured correctly
- [x] .env.example file is present for reference
- [x] All API endpoints tested via Swagger UI and Postman
- [x] CSV import works with sample file
- [x] Bulk status update rolls back on failure
- [x] Reports return correct aggregated data
- [x] Timeline endpoint returns issue history
- [x] README documentation is complete