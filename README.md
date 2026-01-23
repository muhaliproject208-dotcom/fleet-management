# Fleet Management System - Pre-Trip Inspection Module

A comprehensive pre-trip inspection system with 12 modules, PDF report generation, audit logging, and complete REST API.

## 📋 Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [API Documentation](#api-documentation)
- [System Architecture](#system-architecture)
- [Usage Guide](#usage-guide)
- [Testing](#testing)
- [Deployment](#deployment)

## ✨ Features

### Core Modules

1. **Driver Management** - Driver profiles, licenses, and records
2. **Vehicle Management** - Vehicle fleet tracking and maintenance
3. **Mechanic Management** - Mechanic credentials and assignments
4. **Pre-Trip Inspection Core** - Workflow management (draft → submit → approve/reject)

### Inspection Modules (12 Total)

5. **Health & Fitness Checks** - Driver physical/mental fitness validation
6. **Documentation & Compliance** - License, insurance, roadworthiness tracking
7. **Vehicle Exterior Checks** - Body, lights, tires, mirrors
8. **Engine & Fluid Checks** - Oil, coolant, brake fluid levels
9. **Interior & Cabin Checks** - Seats, controls, cleanliness
10. **Functional Checks** - Brakes, steering, horn, wipers
11. **Safety Equipment Checks** - Fire extinguisher, first aid, reflectors
12. **Trip Behavior Monitoring** - Speed violations, incidents, route compliance
13. **Driving Behavior Checks** - Seatbelt, phone usage, fatigue
14. **Post-Trip Reporting** - Faults, incidents, odometer readings
15. **Risk Score Summary** - 30-day rolling risk assessment
16. **Corrective Measures** - Retraining, vehicle repair tracking
17. **Enforcement Actions** - Suspensions, warnings, penalties
18. **Supervisor Remarks** - Comments and recommendations
19. **Evaluation Summary** - 5-criteria scoring (1-5) with auto-calculated performance
20. **Inspection Sign-Offs** - Driver, supervisor, mechanic signatures

### System Features

- ✅ **PDF Report Generation** - Complete inspection reports with watermarks
- ✅ **Audit Logging** - Track all create/update/delete/approve/reject actions
- ✅ **Advanced Filtering** - Date ranges, status, search, critical failures
- ✅ **Dashboard Statistics** - Real-time metrics by role
- ✅ **Role-Based Access Control** - Transport Supervisor, Fleet Manager, Superuser
- ✅ **Nested API Routing** - Clean RESTful structure
- ✅ **Optimized Queries** - select_related, prefetch_related for performance
- ✅ **Custom Error Handling** - Consistent error response format
- ✅ **API Documentation** - Swagger UI and ReDoc

## 🛠️ Technology Stack

### Backend
- **Django 6.0.1** - Web framework
- **Django REST Framework 3.16.1** - API framework
- **PostgreSQL** - Database
- **Supabase** - Authentication & hosting
- **reportlab 4.4.9** - PDF generation
- **drf-yasg 1.21.14** - API documentation
- **django-filter 25.2** - Advanced filtering
- **drf-nested-routers 0.95.0** - Nested routing

### Dependencies
```
Django==6.0.1
djangorestframework==3.16.1
djangorestframework-simplejwt==5.5.1
django-cors-headers==4.9.0
psycopg2-binary==2.9.11
python-decouple==3.8
gotrue==2.12.4
httpx==0.28.1
reportlab==4.4.9
drf-yasg==1.21.14
django-filter==25.2
drf-nested-routers==0.95.0
```

## 💻 System Requirements

- Python 3.14+
- PostgreSQL 12+
- pip 25.2+
- Virtual environment (recommended)

## 🚀 Installation

### 1. Clone Repository

```bash
git clone https://github.com/muhaliproject208-dotcom/fleet-management.git
cd fleet-management/backend
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv myenv
myenv\Scripts\activate

# Linux/Mac
python3 -m venv myenv
source myenv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create `.env` file in `backend/` directory:

```env
# Database
DATABASE_NAME=fleet_management
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
SUPABASE_SERVICE_KEY=your_service_key

# Security
SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# JWT
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 5. Database Setup

```bash
# Create database
psql -U postgres
CREATE DATABASE fleet_management;
\q

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 6. Run Development Server

```bash
python manage.py runserver
```

Server runs at: `http://localhost:8000`

## 📚 API Documentation

### Access Documentation

- **Swagger UI**: http://localhost:8000/api/v1/docs/
- **ReDoc**: http://localhost:8000/api/v1/redoc/
- **JSON Schema**: http://localhost:8000/api/v1/swagger.json

### Key Endpoints

#### Authentication
```
POST /api/v1/auth/login/          - Login and get JWT tokens
POST /api/v1/auth/register/       - Register new user
POST /api/v1/auth/refresh/        - Refresh access token
POST /api/v1/auth/logout/         - Logout
```

#### Inspections
```
GET    /api/v1/inspections/                     - List inspections (filtered by role)
POST   /api/v1/inspections/                     - Create new inspection
GET    /api/v1/inspections/{id}/                - Get full inspection details
PATCH  /api/v1/inspections/{id}/                - Update inspection
POST   /api/v1/inspections/{id}/submit/         - Submit for approval
POST   /api/v1/inspections/{id}/approve/        - Approve inspection (Fleet Manager)
POST   /api/v1/inspections/{id}/reject/         - Reject inspection (Fleet Manager)
GET    /api/v1/inspections/{id}/download_pdf/   - Download PDF report
GET    /api/v1/inspections/dashboard_stats/     - Dashboard statistics
```

#### Inspection Sub-Modules (Nested Routes)
```
POST /api/v1/inspections/{id}/health-fitness/      - Add health check
POST /api/v1/inspections/{id}/documentation/       - Add documentation
POST /api/v1/inspections/{id}/exterior-checks/     - Add exterior checks (bulk)
POST /api/v1/inspections/{id}/engine-checks/       - Add engine checks (bulk)
POST /api/v1/inspections/{id}/interior-checks/     - Add interior checks (bulk)
POST /api/v1/inspections/{id}/functional-checks/   - Add functional checks (bulk)
POST /api/v1/inspections/{id}/safety-checks/       - Add safety checks (bulk)
POST /api/v1/inspections/{id}/trip-behaviors/      - Add trip behaviors (bulk)
POST /api/v1/inspections/{id}/driving-behaviors/   - Add driving behaviors (bulk)
POST /api/v1/inspections/{id}/post-trip/           - Add post-trip report
POST /api/v1/inspections/{id}/risk-score/          - Add risk score
POST /api/v1/inspections/{id}/corrective-measures/ - Add corrective measures
POST /api/v1/inspections/{id}/enforcement-actions/ - Add enforcement actions
POST /api/v1/inspections/{id}/supervisor-remarks/  - Add supervisor remarks
POST /api/v1/inspections/{id}/evaluation/          - Add evaluation
POST /api/v1/inspections/{id}/sign-offs/           - Add sign-off
```

#### Drivers
```
GET  /api/v1/drivers/       - List drivers
POST /api/v1/drivers/       - Create driver
GET  /api/v1/drivers/{id}/  - Get driver details
```

#### Vehicles
```
GET  /api/v1/vehicles/       - List vehicles
POST /api/v1/vehicles/       - Create vehicle
GET  /api/v1/vehicles/{id}/  - Get vehicle details
```

### Filtering & Search

**Query Parameters:**
```
# Status filter
?status=draft|submitted|approved|rejected

# Date range
?inspection_date_from=2026-01-01&inspection_date_to=2026-01-31

# Search
?search=ABC123  (searches inspection_id, driver name, vehicle reg)

# Driver/Vehicle filter
?driver=1&vehicle=2

# Critical failures
?has_critical_failures=true

# Ordering
?ordering=-created_at
```

## 🏗️ System Architecture

### Database Models (20 Total)

#### Core Models
- `User` - Authentication users with roles
- `Driver` - Driver profiles and licenses
- `Vehicle` - Vehicle fleet records
- `Mechanic` - Mechanic credentials
- `PreTripInspection` - Main inspection with workflow

#### Inspection Sub-Models (OneToOne)
- `HealthFitnessCheck`
- `DocumentationCompliance`
- `PostTripReport`
- `RiskScoreSummary`
- `SupervisorRemarks`
- `EvaluationSummary`

#### Inspection Sub-Models (ForeignKey)
- `VehicleExteriorCheck`
- `EngineFluidCheck`
- `InteriorCabinCheck`
- `FunctionalCheck`
- `SafetyEquipmentCheck`
- `TripBehaviorMonitoring`
- `DrivingBehaviorCheck`
- `CorrectiveMeasure`
- `EnforcementAction`
- `InspectionSignOff`

#### System Models
- `AuditLog` - Audit trail

### Workflow States

```
draft → submitted → approved
  ↓                    ↓
rejected ←────────────┘
```

**State Transitions:**
- `draft` - Initial state, editable
- `submitted` - Awaiting approval, read-only
- `approved` - Approved by fleet manager, locked
- `rejected` - Rejected with reason, editable after resubmission

## 📖 Usage Guide

### 1. Create Inspection

```python
POST /api/v1/inspections/
{
  "driver": 1,
  "vehicle": 2,
  "trip_date": "2026-01-24",
  "route": "Lusaka to Ndola",
  "planned_departure_time": "08:00:00"
}
```

### 2. Add Health Check

```python
POST /api/v1/inspections/1/health-fitness/
{
  "physical_fitness": "pass",
  "mental_alertness": "pass",
  "substance_check": "pass",
  "adequate_rest": "pass"
}
```

### 3. Add Vehicle Checks (Bulk)

```python
POST /api/v1/inspections/1/exterior-checks/bulk_create/
{
  "checks": [
    {"check_item": "body_damage", "status": "pass"},
    {"check_item": "headlights", "status": "pass"},
    {"check_item": "tire_condition", "status": "pass", "is_critical_failure": true}
  ]
}
```

### 4. Submit for Approval

```python
POST /api/v1/inspections/1/submit/
```

**Validation Rules:**
- ✅ Health & Fitness: All checks must pass
- ✅ Documentation: All documents must be valid
- ✅ No critical failures in vehicle checks
- ✅ Supervisor sign-off required

### 5. Approve Inspection (Fleet Manager)

```python
POST /api/v1/inspections/1/approve/
```

### 6. Download PDF Report

```python
GET /api/v1/inspections/1/download_pdf/
```

**Response:** PDF file download

**PDF Features:**
- Watermarks for draft/rejected
- Color-coded status indicators
- Complete 17-section report
- Signature placeholders
- Page numbers and timestamps

## 🧪 Testing

### Unit Tests

```bash
python manage.py test inspections
```

### API Testing with Postman

1. Import Postman collection (see `/docs/postman_collection.json`)
2. Set environment variables:
   - `base_url`: http://localhost:8000
   - `access_token`: (obtain from login)
3. Run collection

### Test Checklist

- [ ] User registration and login
- [ ] Create inspection (all roles)
- [ ] Fill all 12 inspection modules
- [ ] Submit inspection with validation
- [ ] Approve/reject workflow
- [ ] PDF generation
- [ ] Dashboard statistics
- [ ] Filtering and search
- [ ] Audit logging
- [ ] Permission checks (role-based)

## 🚢 Deployment

### Production Settings

1. **Update `.env`:**
```env
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
SECRET_KEY=your_production_secret_key
```

2. **Collect Static Files:**
```bash
python manage.py collectstatic
```

3. **Database Backup:**
```bash
pg_dump fleet_management > backup.sql
```

### Deploy to Render/Railway/Heroku

See `/docs/deployment_guide.md` for platform-specific instructions.

## 📊 Performance Optimizations

1. **Query Optimization**
   - `select_related()` for OneToOne/ForeignKey
   - `prefetch_related()` for reverse ForeignKey
   - Database indexes on frequently queried fields

2. **Caching** (Future)
   - Redis for API response caching
   - Cache dashboard statistics

3. **Background Tasks** (Future)
   - Celery for PDF generation
   - Scheduled risk score recalculation

## 🔐 Security

- JWT token authentication
- Role-based permissions
- CORS configuration
- SQL injection protection (ORM)
- XSS protection (Django templates)
- CSRF protection
- Audit logging for compliance

## 📝 License

Proprietary - All rights reserved

## 👥 Support

For support, email support@fleetmanagement.com or create an issue in the repository.

## 🎯 Roadmap

- [ ] Mobile app (React Native)
- [ ] Real-time notifications (WebSockets)
- [ ] Advanced analytics dashboard
- [ ] Integration with vehicle telematics
- [ ] Multi-tenant support
- [ ] Offline mode for mobile app
- [ ] Automated report scheduling
- [ ] Machine learning for risk prediction

---

**Version:** 1.0.0  
**Last Updated:** January 23, 2026  
**Built with ❤️ for Fleet Management**
