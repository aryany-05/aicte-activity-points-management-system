# AICTE Activity & Points Management System

An institutional web platform designed for colleges to manage student co-curricular activities, track earned activity points across standard AICTE activity categories, verify attendance, and issue verifiable participation certificates and audit reports.

---

## 1. Overview

The **AICTE Activity & Points Management System** streamlines the management of co-curricular achievements. Under AICTE guidelines, engineering students participate in extracurricular and co-curricular programs to earn activity points. This platform provides:
- A unified student portal to discover institutional activities, register, and track cumulative point balances.
- A club management workspace for student organizations to propose activities, manage attendee rosters, and configure authorized certificate signatures.
- An administrative operations console for college administrators to sanction activity proposals, monitor user accounts, and review institutional leaderboards.
- Automated generation of single-page A4 landscape participation certificates and comprehensive student activity audit reports.

---

## 2. Core Features

### 🎓 Student Portal
- **Dashboard & Progress Tracking**: Real-time summary of accumulated activity points with a visual breakdown across the four AICTE activity categories (Technical, Cultural, Social, Sports).
- **Activity Registry**: Discover approved college activities with category filtering, schedule and venue details, and live search.
- **Activity Registration**: One-click registration for upcoming approved events with automatic seat allocation and duplicate prevention.
- **Attendance & Activity Ledger**: Chronological ledger of registered and attended activities with awarded point values.
- **Student Activity Report**: Download an audit-ready PDF summary of all attended activities and category totals.
- **Participation Certificates**: Download institutional participation certificates for attended events.

### 🏛️ Club Operations Console
- **Club Dashboard**: Overview metrics tracking active events, approved proposals, pending reviews, and total participant registrations.
- **Activity Proposal Workspace**: Structured event proposal submission form including title, category, date, time, campus venue, point allocation (1–20 pts), and participant capacity.
- **Attendance Verification**: Attendee roster management for club events with status badges, search filter, and individual or bulk attendance marking.
- **QR Code Verification**: Automated generation of unique event QR code tokens for venue check-ins.
- **Certificate Signature Management**: Dedicated signatory settings workspace allowing clubs to upload, preview, and update authorized digital signatures (Event Organizer and Administration) rendered directly on certificates.

### 🛡️ Administration Operations Console
- **Operations Console**: High-level institutional metrics, pending activity proposals awaiting review, and system-wide activity ledger.
- **Sanction Workflow**: Review submitted club activity proposals with one-click approval or rejection with documented feedback.
- **User Directory**: Central directory of all registered accounts (Students, Clubs, Administrators) with instant keyword filtering and role tabs.
- **Institutional Leaderboard**: Academic standings ledger ranking students by verified accumulated activity points.
- **Role-Based Access Control**: Strict server-side route guards enforcing boundaries across all user types.

---

## 3. Technology Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Backend Framework** | Python 3.8+ / Flask 3.1.0 | Lightweight WSGI web application framework |
| **Database** | MySQL 8.0+ | Relational database management system |
| **Database Connector** | `mysql-connector-python` | Official Oracle MySQL driver with connection pooling |
| **Authentication & Security** | `bcrypt` | Blowfish password hashing algorithm |
| **Document Generation** | `reportlab` (4.2.5) | Low-level PDF generation engine for certificates and reports |
| **QR Code Generation** | `qrcode[pil]` & `Pillow` | Dynamic QR code rendering and image processing |
| **Configuration** | `python-dotenv` | Environment variable management via `.env` |
| **WSGI Server** | `gunicorn` (22.0.0) | Production WSGI HTTP server |
| **Frontend Styling** | Vanilla CSS (CSS3) | Design system with light/dark theme support |
| **Typography** | Plus Jakarta Sans & Space Grotesk | High-legibility institutional typography |
| **Icons** | Lucide Icons | Accessible SVG icon suite |

---

## 4. User Roles

The application enforces three distinct user roles:

1. **Student (`role: 'student'`)**:
   - Access: `/student/dashboard`, `/student/events`, `/student/leaderboard`, `/student/report`, `/student/certificate/<id>`
   - Permissions: Browse events, register for upcoming approved events, view personal point totals, download personal activity reports and earned certificates. Cannot access club management or administration pages.
2. **Club (`role: 'club'`)**:
   - Access: `/club/dashboard`, `/club/event/create`, `/club/event/<id>/attendees`, `/club/certificate-settings`
   - Permissions: Create and edit club event proposals, view registered attendees for owned events, mark attendance, and configure certificate signatures. Cannot mark attendance on other clubs' events or access admin console.
3. **Administrator (`role: 'admin'`)**:
   - Access: `/admin/dashboard`, `/admin/users`, `/admin/leaderboard`, `/admin/event/<id>/approve`, `/admin/event/<id>/reject`
   - Permissions: Review and approve/reject submitted activity proposals, view user directory, and inspect full institutional leaderboard.

---

## 5. Project Structure

```
aicte-points-website/
├── app.py                      # Flask application factory, error handlers, and route registration
├── config.py                   # Centralized configuration, path constants, and DB settings
├── requirements.txt            # Python package dependencies
├── schema.sql                  # MySQL database schema, constraints, and seed data
├── Procfile                    # Production process definition for Gunicorn deployment
├── .env.example                # Sample environment configuration template
├── .gitignore                  # Git exclusion rules for virtual environments and runtime files
├── README.md                   # Project documentation
├── setup_instructions.md       # Step-by-step Windows local installation guide
├── models/                     # Database models and business logic
│   ├── database.py             # MySQL connection pool helper
│   ├── user.py                 # User authentication, role filtering, and leaderboard queries
│   ├── event.py                # Activity CRUD, approval lifecycle, and attendee rosters
│   └── registration.py         # Registration tracking, attendance verification, and points
├── routes/                     # Blueprint route controllers
│   ├── auth.py                 # Login, signup, and logout endpoints
│   ├── student.py              # Student dashboard, event registry, reports, and certificates
│   ├── club.py                 # Club console, event proposal, attendance, and signatures
│   └── admin.py                # Admin console, moderation actions, and user directory
├── utils/                      # Helper libraries and utilities
│   ├── pdf_generator.py        # ReportLab PDF builders for reports and certificates
│   ├── qr_generator.py         # QR code token generation
│   ├── rate_limiter.py         # In-memory IP rate limiter for login protection
│   └── validators.py           # Form validation and input sanitization helpers
├── templates/                  # Jinja2 HTML templates
│   ├── base.html               # Shared layout, navigation bar, flash alerts, and footer
│   ├── index.html              # Public landing page
│   ├── auth/                   # Authentication views (login, signup)
│   ├── student/                # Student portal views (dashboard, events, leaderboard)
│   ├── club/                   # Club views (dashboard, proposal, attendance, settings)
│   ├── admin/                  # Admin views (dashboard, users, leaderboard)
│   └── errors/                 # Error response views (404, 500)
├── static/                     # Static web assets
│   ├── css/style.css           # Complete institutional design system and dark theme styles
│   ├── js/main.js              # Theme switcher, navigation toggle, and live table search
│   ├── certificates/           # Directory for generated certificate PDFs (runtime)
│   ├── reports/                # Directory for generated student reports (runtime)
│   └── qrcodes/                # Directory for generated QR codes (runtime)
└── uploads/                    # User-uploaded content
    └── signatures/             # Authorized club and administration signature PNGs
```

---

## 6. Database Architecture

The application uses a relational schema in MySQL (`aicte_db`):

- **`users` Table**: Stores accounts with `username`, `email`, `password_hash` (bcrypt), `role` (`student`, `club`, `admin`), `full_name`, and role-specific fields (`department`, `roll_number`, `club_name`).
- **`events` Table**: Stores activity proposals with `title`, `description`, `category` (`technical`, `cultural`, `social`, `sports`), `event_date`, `event_time`, `venue`, `points` (1–20), `max_participants`, `status` (`pending`, `approved`, `rejected`), `rejection_reason`, and `qr_token`. Foreign key references `users(id)`.
- **`registrations` Table**: Junction table linking students to events with `student_id`, `event_id`, `registered_at`, `attended` (0 or 1), `points_awarded`, and `attendance_marked_at`. Enforces a unique compound key `(student_id, event_id)` to prevent duplicate registrations.

---

## 7. Installation & Setup

### Prerequisites
- Python **3.8+** (Python 3.10+ recommended)
- MySQL Server **8.0+**
- Git (optional)

### Setup Steps (Windows)

1. **Clone or extract** the repository into a directory:
   ```cmd
   cd aicte-points-website-main
   ```

2. **Create and activate a virtual environment**:
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```cmd
   pip install -r requirements.txt
   ```

4. **Initialize the MySQL database**:
   - Start your MySQL server.
   - Run the initialization script using the MySQL client:
     ```cmd
     mysql -u root -p < schema.sql
     ```
   *(Enter your MySQL password when prompted. If root has no password, omit `-p` or press Enter).*

5. **Configure environment variables**:
   - Copy `.env.example` to `.env`:
     ```cmd
     copy .env.example .env
     ```
   - Update `.env` with your MySQL credentials:
     ```ini
     MYSQL_HOST=localhost
     MYSQL_PORT=3306
     MYSQL_USER=root
     MYSQL_PASSWORD=your_actual_mysql_password
     MYSQL_DATABASE=aicte_db
     SECRET_KEY=your_random_flask_secret_key
     FLASK_ENV=development
     SESSION_COOKIE_SECURE=false
     ```

---

## 8. Running the Application

Start the Flask development server:
```cmd
python app.py
```

The application will start on:
```
http://127.0.0.1:5000
```

To stop the server, press `CTRL + C` in the terminal.

---

## 9. Demo Accounts

The database seed in `schema.sql` provides pre-configured demo accounts for testing:

| Role | Username | Password | Purpose |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin` | `admin123` | Institutional dashboard, event sanctions, user management |
| **Club Organizer** | `techclub` | `club123` | Event proposal creation, attendance verification, signatures |
| **Student** | `rahul` | `student123` | Event registration, point tracking, certificates |
| **Student** | `priya` | `student123` | Secondary student account for multi-user tests |

---

## 10. Security Controls

The application implements the following verified security controls:
- **Password Security**: Passwords are encrypted using `bcrypt` with adaptive cost salt rounds before database storage. Raw passwords are never persisted.
- **SQL Injection Prevention**: All database queries use parameterized SQL `%s` statements via `mysql.connector`. No dynamic SQL concatenation is used.
- **Server-Side Authentication**: Session authentication is stored server-side. Sensitive data like `password_hash` is stripped from dictionary outputs and template contexts.
- **Role-Based Authorization**: Every protected route enforces `@student_required`, `@club_required`, or `@admin_required` decorators.
- **Object Ownership Verification**: Clubs can only view rosters and mark attendance for events they own.
- **Input Sanitization**: Form inputs are validated and sanitized via `utils/validators.py`.
- **Upload Restrictions**: Certificate signature uploads enforce strict extension checks (`.png`, `.jpg`, `.jpeg`), image binary header verification via Pillow, and a 2MB maximum file size ceiling. Signatures are namespaced by club ID (`uploads/signatures/club_<id>/`).
- **Session Protection**: Cookies are configured with `HttpOnly=True` and `SameSite='Lax'` to protect against cross-site scripting and unauthorized transmission.
- **Brute-Force Rate Limiting**: The login endpoint incorporates an IP-based rate limiter (`utils/rate_limiter.py`) restricting excessive failed login attempts.

---

## 11. Certificate Generation

Participation certificates are compiled on demand using ReportLab:
- **Format**: Single-page A4 landscape layout.
- **Eligibility**: Certificates can only be generated for events where the student has verified attendance (`attended = 1`).
- **Signatory Options**: Supports 4 distinct signature configurations based on club settings:
  1. Default: Architectural signatory rules with printed role titles.
  2. Event Organizer Only: Renders scaled club organizer signature.
  3. Administration Only: Renders scaled college administration signature.
  4. Dual Signatures: Renders both signatures aligned above their respective signatory lines.
- **Layout Resilience**: Text styling dynamically wraps and scales long student names, complex event titles, and long venues to preserve single-page layout without spillover.

---

## 12. Project Status

- **Development**: Complete (Phases 1–5D).
- **Quality Assurance**: 100% test pass rate across unit, integration, and end-to-end regression suites (Phase 6).
- **Repository Health**: Cleaned of temporary files, backup directories, and cached artifacts (Phase 7).
- **Readiness**: Validated for institutional deployment and demonstration.
