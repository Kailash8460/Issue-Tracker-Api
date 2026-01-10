# TEST_CASES.md

# Issue Tracker API – Test Cases

This document contains complete functional test cases executed for the Issue Tracker API.
All endpoints were tested using **Swagger UI** and **Postman**.

---

## 1. Users API

### 1.1 Create User (Success)
**Endpoint:** `POST /users/`

**Request**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "mobile_number": "9876543210",
  "password": "strongpass123"
}
```

**Expected Result**
- Status Code: 201
- User created successfully
- Password not returned

**Result:** PASS

**Response**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "mobile_number": "9876543210"
}
```

---

### 1.2 Create User (Duplicate Email)
**Endpoint:** `POST /users/`

**Request**
```json
{
  "username": "john_doe2",
  "email": "john@example.com",
  "password": "password123"
}
```

**Expected Result**
- Status Code: 400
- Duplicate email error

**Result:** PASS

**Response**
```json
{
  "detail": "Username or email already registered"
}
```

---

## 2. Issues API

### 2.1 Create Issue
**Endpoint:** `POST /issues/`

**Request**
```json
{
  "title": "Login Bug",
  "description": "Login button not responding",
  "priority": "high",
  "assignee_id": 1
}
```

**Expected Result**
- Status Code: 201
- status = open
- version = 1

**Result:** PASS

**Response**
```json
{
  "id": 1,
  "title": "Login Bug",
  "description": "Login button not responding",
  "status": "open",
  "priority": "high",
  "assignee_id": 1,
  "version": 1
}
```

---

### 2.2 Update Issue (Resolved)
**Endpoint:** `PATCH /issues/{issue_id}` 

**Request**
```json
{
  "status": "resolved",
  "version": 1
}
```

**Expected Result**
- Status Code: 200
- resolved_at set
- version incremented

**Result:** PASS

**Response**
```json
{
  "id": 1,
  "status": "resolved",
  "version": 2,
  "resolved_at": "2026-01-10T10:00:00"
}
```

---

### 2.3 Update Issue (Version Conflict)
**Endpoint:** `PATCH /issues/{issue_id}`

**Request**
```json
{
  "status": "closed",
  "version": 1
}
```

**Expected Result**
- Status Code: 409
- Version conflict error

**Result:** PASS

**Response**
```json
{
  "detail": "Version conflict: Issue has been modified by another process"
}
```

---

### 2.4 List Issues with Filters, Sorting & Pagination
**Endpoint:** `GET /issues`

**Query Params**
```
status=open
priority=high
page=1
page_size=10
sort_by=created_at
sort_order=desc
```

**Expected Result**
- Status Code: 200
- Filtered issues returned
- Pagination metadata present

**Result:** PASS

**Response**
```json
{
  "total": 1,
  "page": 1,
  "page_size": 10,
  "issues": [
    {
      "id": 1,
      "title": "Login Bug",
      "status": "open",
      "priority": "high"
    }
  ]
}
```

---

## 3. Comments API

### 3.1 Add Comment
**Endpoint:** `POST /issues/{issue_id}/comments` 

**Request**
```json
{
  "content": "Investigating the issue",
  "author_id": 1
}
```

**Expected Result**
- Status Code: 201
- Comment created

**Result:** PASS

**Response**
```json
{
  "id": 1,
  "content": "Investigating the issue",
  "issue_id": 1,
  "author_id": 1
}
```

---

### 3.2 List Comments with Pagination & Filters
**Endpoint:** `GET /issues/{issue_id}/comments`

**Query Params**
```
page=1
page_size=5
sort_order=desc
```

**Expected Result**
- Status Code: 200
- Paginated comments returned

**Result:** PASS

**Response**
```json
{
  "total": 1,
  "page": 1,
  "page_size": 5,
  "comments": [
    {
      "id": 1,
      "content": "Investigating the issue"
    }
  ]
}
```

---

## 4. Labels API

### 4.1 Replace Issue Labels
**Endpoint:** `PUT /issues/{issue_id}/labels`

**Request**
```json
{
  "label_ids": [1, 2]
}
```

**Expected Result**
- Status Code: 200
- Labels replaced successfully

**Result:** PASS

**Response**
```json
{
  "total": 2,
  "labels": [
    {
      "id": 1,
      "name": "bug"
    },
    {
      "id": 2,
      "name": "urgent"
    }
  ]
}
```

---

## 5. Bulk Status Update

### 5.1 Bulk Resolve Issues
**Endpoint:** `POST /issues/bulk-status`

**Request**
```json
{
  "issue_ids": [1],
  "status": "resolved"
}
```

**Expected Result**
- Status Code: 200
- All issues resolved

**Result:** PASS

**Response**
```json
{
  "total": 1,
  "issues": [
    {
      "id": 1,
      "status": "resolved"
    }
  ]
}
```

---

### 5.2 Bulk Close Issues (Rollback)
**Endpoint:** `POST /issues/bulk-status`

**Request**
```json
{
  "issue_ids": [1, 2],
  "status": "closed"
}
```

**Expected Result**
- Status Code: 400
- Transaction rolled back

**Result:** PASS

**Response**
```json
{
  "detail": "Issue ID 1 must be resolved before closing"
}
```

---

## 6. CSV Import

### 6.1 Import Issues via CSV
**Endpoint:** `POST /issues/import-csv`

**Request**
- **Input File:** Sample Data Flow.csv

**Expected Result**
- Status Code: 201
- Valid rows imported
- Invalid rows skipped with report

**Result:** PASS

**Response**
```json
{
    "total_rows": 4,
    "created_issues": 3,
    "failed_rows": 1,
    "errors": [
        {
            "row": 4,
            "error": "Invalid priority 'urgent'. Must be one of {'low', 'high', 'medium', 'critical'}."
        }
    ]
}
```

---

## 7. Reports API

### 7.1 Top Assignees
**Endpoint:** `GET /reports/top-assignees`

**Expected Result**
- Status Code: 200
- Aggregated assignee data returned

**Result:** PASS

**Response**
```json
[
  {
    "assignee_id": 1,
    "assignee_name": "john_doe",
    "issue_count": 3
  }
]
```

---

### 7.2 Average Resolution Time
**Endpoint:** `GET /reports/average-latency`

**Expected Result**
- Status Code: 200
- Average resolution time returned

**Result:** PASS

**Response**
```json
{
  "average_latency_hours": 12.5
}
```

---

## 8. Timeline API

### 8.1 Issue Timeline
**Endpoint:** `GET /issues/{issue_id}/timeline`

**Expected Result**
- Status Code: 200
- Chronological list of issue events

**Result:** PASS

**Response**
```json
[
  {
    "event_type": "status_change",
    "old_value": "open",
    "new_value": "resolved"
  }
]
```
