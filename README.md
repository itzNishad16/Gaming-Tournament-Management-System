# 🎮 Gaming Tournament Management System

A database-driven web application designed to simplify the management of gaming tournaments, players, teams, matches, and results. The system provides a centralized platform for organizing tournaments and managing tournament-related information efficiently.

## 📌 Overview

Managing gaming tournaments manually can become complicated when handling player registrations, team formation, match scheduling, and results. This project aims to streamline these operations through a simple web-based management system backed by a relational database.

The application is developed using **Python, Streamlit, and MySQL**, providing an interactive interface and structured data management.

## ✨ Features

- **Player Management** – Manage player information and registrations.
- **Tournament Management** – Create and organize gaming tournaments.
- **Team Management** – Create teams and manage team members.
- **Match Management** – Organize matches and maintain match information.
- **Result Management** – Record and manage match results.
- **Database Integration** – Store and manage data using MySQL.
- **Interactive Interface** – Access the system through a Streamlit web interface.

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Backend logic and application development |
| Streamlit | Web interface |
| MySQL | Relational database management |
| mysql-connector-python | Python–MySQL connectivity |

## 🏗️ System Architecture

The application follows a simple three-layer structure:

- **Presentation Layer:** Streamlit interface for user interaction.
- **Application Layer:** Python logic for handling operations and application workflows.
- **Database Layer:** MySQL database for storing and managing tournament data.

## 🗄️ Database Structure

The system uses a MySQL database named `gaming_tournament_db`.

The database consists of the following tables:

| Table | Description |
|---|---|
| `users` | Stores user account information |
| `players` | Stores player details |
| `games` | Stores game information |
| `tournaments` | Stores tournament details |
| `teams` | Stores team information |
| `team_members` | Maintains team-player relationships |
| `matches` | Stores match details |
| `match_results` | Stores match outcomes and results |

## 📂 Project Structure

```text
GamingTournamentManager/
│
├── database/
│   └── schema.sql
│
├── app/
│   ├── main.py
│   └── db.py
│
├── .env
├── requirements.txt
└── README.md
```

## ⚙️ Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/GamingTournamentManager.git
```

### 2. Navigate to the project directory

```bash
cd GamingTournamentManager
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure MySQL

Ensure MySQL Server is installed and running.

Create the database and tables by executing the SQL script:

```sql
SOURCE database/schema.sql;
```

Run the command above inside the MySQL command-line client after navigating to the project directory, or import the SQL file through MySQL Workbench.

### 5. Configure environment variables

Create a `.env` file in the project root directory and configure your MySQL credentials:

```env
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=gaming_tournament_db
```

Replace `your_mysql_password` with your actual MySQL password.

**Do not upload your `.env` file or expose database credentials on GitHub.**

### 6. Run the application

```bash
streamlit run app/main.py
```

The application will be available in your browser at:

```text
http://localhost:8501
```

## 🚀 Usage

Once the application is running, users can interact with the system through the web interface to manage gaming tournament-related data, including players, games, tournaments, teams, matches, and results.

## 🎯 Project Objectives

- Simplify gaming tournament organization and management.
- Centralize tournament-related data.
- Reduce manual record-keeping.
- Maintain structured player, team, match, and result information.
- Demonstrate the integration of Python-based applications with relational databases.

## 🔮 Future Scope

- Automated tournament bracket generation.
- Real-time score updates.
- Leaderboards and player rankings.
- Tournament statistics and analytics.
- Enhanced user authentication and role-based access control.
- Improved dashboard and visualization features.

---

<p align="center">
  Developed as an academic project using Python, Streamlit, and MySQL.
</p>
