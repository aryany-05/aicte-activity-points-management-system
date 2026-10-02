# Complete Local Setup Guide (Windows)

This guide walks you through setting up and running the **AICTE Activity & Points Management System** from scratch on a Windows machine.

---

## 1. Prerequisites

Before starting, ensure you have the following installed on your machine:
- **Python 3.8+** (Python 3.10, 3.11, 3.12, or 3.13 recommended): [Download Python](https://www.python.org/downloads/)
  - *Important during installation*: Check the box labeled **"Add python.exe to PATH"**.
- **MySQL Community Server 8.0+**: [Download MySQL Installer](https://dev.mysql.com/downloads/installer/)
  - Note down the `root` user password you configure during MySQL installation.
- **Git** (optional, if cloning via command line): [Download Git](https://git-scm.com/)

---

## 2. Project Directory Extraction

Extract the downloaded ZIP file or clone the project repository into your preferred folder:

```cmd
cd "C:\Users\<YourUsername>\Downloads\aicte-points-website-main"
```

Verify you are in the directory containing `app.py`, `config.py`, `requirements.txt`, and `schema.sql`.

---

## 3. Verify Python Installation

Open **Command Prompt** (`cmd.exe`) or **PowerShell** and verify Python is accessible:

```cmd
python --version
pip --version
```

If the command is not recognized, re-run the Python installer and ensure "Add Python to PATH" is checked, or add your Python installation directory to your Windows System PATH.

---

## 4. Create a Virtual Environment

Isolate the project dependencies by creating a dedicated virtual environment:

```cmd
python -m venv venv
```

This creates a `venv` directory containing a clean Python environment.

---

## 5. Activate the Virtual Environment

Activate the virtual environment in your terminal:

**Command Prompt (`cmd.exe`)**:
```cmd
venv\Scripts\activate.bat
```

**PowerShell**:
```powershell
.\venv\Scripts\Activate.ps1
```
*(If PowerShell displays a script execution policy error, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` once, then re-run the activation command).*

Upon successful activation, `(venv)` will precede your terminal prompt.

---

## 6. Install Project Dependencies

With the virtual environment active, install all required packages:

```cmd
pip install --upgrade pip
pip install -r requirements.txt
```

Verify packages installed without errors:
- `Flask==3.1.0`
- `mysql-connector-python==9.1.0`
- `bcrypt==4.2.1`
- `qrcode[pil]==8.0`
- `reportlab==4.2.5`
- `Pillow>=11.1.0`
- `python-dotenv==1.0.1`
- `gunicorn==22.0.0`

---

## 7. Verify MySQL Server

Ensure your MySQL server is running. You can check the Windows Services application (`services.msc`) for **MySQL** or **MySQL80** status, or run:

```cmd
mysql -u root -p
```
Type your MySQL password. Once inside the MySQL shell, type `exit` to return to your command prompt.

---

## 8. Initialize Database and Import Schema

Import the complete database structure, tables, and sample data using `schema.sql`:

```cmd
mysql -u root -p < schema.sql
```
*(Enter your MySQL root password when prompted)*.

The script automatically:
1. Creates the database `aicte_db` (if it does not already exist).
2. Sets up `users`, `events`, and `registrations` tables with relational integrity and constraints.
3. Inserts pre-configured demo data (administrators, clubs, students, events, and registrations).

---

## 9. Configure Environment Variables (`.env`)

1. Create your local `.env` file by copying `.env.example`:
   ```cmd
   copy .env.example .env
   ```

2. Open `.env` in any text editor (Notepad, VS Code) and update the values to match your MySQL setup:
   ```ini
   MYSQL_HOST=localhost
   MYSQL_PORT=3306
   MYSQL_USER=root
   MYSQL_PASSWORD=your_actual_mysql_password
   MYSQL_DATABASE=aicte_db
   SECRET_KEY=generate_a_random_secret_string_here
   FLASK_ENV=development
   SESSION_COOKIE_SECURE=false
   ```
   *(Replace `your_actual_mysql_password` with your real MySQL password. If your MySQL root account has no password, leave `MYSQL_PASSWORD=` blank)*.

---

## 10. Start the Application

Run the Flask application:

```cmd
python app.py
```

You should see terminal output confirming:
```
============================================================
  AICTE Activity & Points Management System
  Running on http://localhost:5000
============================================================
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

---

## 11. Open in Browser

Open your web browser and navigate to:
```
http://127.0.0.1:5000
```
or
```
http://localhost:5000
```

You will see the AICTE Activity & Points Management System landing page.

---

## 12. Pre-Configured Demo Accounts

Use any of these demo accounts created by `schema.sql`:

| Role | Username | Password | Notes |
| :--- | :--- | :--- | :--- |
| **System Administrator** | `admin` | `admin123` | Institutional dashboard, activity approvals, user management |
| **Club Lead** | `techclub` | `club123` | Create activity proposals, mark attendance, signature settings |
| **Student** | `rahul` | `student123` | Register for events, view points breakdown, download certificates |
| **Student** | `priya` | `student123` | Secondary student account |

---

## 13. Troubleshooting Common Issues

### Issue 1: `mysql.connector.errors.ProgrammingError: 1045: Access denied for user 'root'@'localhost'`
- **Cause**: Incorrect MySQL password in your `.env` file.
- **Fix**: Open `.env` and verify that `MYSQL_PASSWORD` matches the password you entered during MySQL Server installation.

### Issue 2: `mysql.connector.errors.DatabaseError: 1049: Unknown database 'aicte_db'`
- **Cause**: `schema.sql` was not imported.
- **Fix**: Re-run `mysql -u root -p < schema.sql` to construct the database.

### Issue 3: `ModuleNotFoundError: No module named 'flask'`
- **Cause**: Virtual environment is not activated.
- **Fix**: Run `venv\Scripts\activate` in your terminal and ensure `(venv)` appears before running `python app.py`.

### Issue 4: `Address already in use` or Port 5000 blocked
- **Cause**: Another service or previous Python process is occupying port 5000.
- **Fix**: In Windows Command Prompt, run:
  ```cmd
  netstat -ano | findstr :5000
  ```
  Note the PID number at the end of the line, then kill the process:
  ```cmd
  taskkill /PID <PID_NUMBER> /F
  ```
  Then restart `python app.py`.

---

## 14. Stopping the Application

To shut down the development server, press `CTRL + C` in the command prompt window where `app.py` is running.
To deactivate the virtual environment, run:
```cmd
deactivate
```
