# TracBee – Job Discovery & Skill Demand Platform

A Django-powered job discovery platform that helps users explore job opportunities, discover in-demand skills, and understand hiring trends.

🌐 **Live Demo:** https://tracbee.onrender.com  
💻 **GitHub Repository:** https://github.com/Kaushar718/TracBee

## 📌 Overview

TracBee is a web-based job discovery platform designed to make job searching and skill-demand exploration easier.

It brings job listings and skill-demand insights together in one place, helping users understand the job market and explore relevant opportunities.

## ✨ Key Features

- **Job Discovery:** Browse available job opportunities.
- **Job Search:** Explore job listings and filter opportunities.
- **Skill Demand Analysis:** Discover skills appearing in job postings.
- **Analytics Dashboard:** View job-market statistics and insights.
- **Job Trends:** Explore hiring and skill trends.
- **Job Details:** View detailed information about individual jobs.
- **REST API:** Access job and skill-demand data through API endpoints.
- **Responsive Interface:** Access the platform through a web browser.

## 📊 Project Statistics

- 281 total job postings imported.
- 269 active job postings displayed.
- 13 skills tracked.
- Deployed using Render.

*Statistics reflect the database at the time of documentation.*

## 🛠️ Tech Stack

- **Backend:** Python, Django
- **API:** Django REST Framework
- **Database:** PostgreSQL (production), SQLite (local development, if configured)
- **Frontend:** HTML, CSS, JavaScript
- **Deployment:** Render
- **Version Control:** Git & GitHub

## 🔗 API Endpoints

| Endpoint | Description |
|---|---|
| `/api/jobs/` | Retrieve job listings |
| `/api/skills/demand/` | Retrieve skill-demand data |

## 🚀 Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/Kaushar718/TracBee.git
cd TracBee
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Configure your Django secret key, debug setting, allowed hosts, and database settings for your local environment.

Never commit production secrets or database credentials.

### 5. Apply migrations

```bash
python manage.py migrate
```

### 6. Start the development server

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

## ☁️ Deployment

TracBee is deployed on Render.

Live application: https://tracbee.onrender.com

The production database uses PostgreSQL.

## 🎯 Project Goal

The goal of TracBee is to make job discovery and skill-demand insights more accessible while providing a practical platform for exploring employment opportunities.

## 👨‍💻 Developer

**Kaushar Shaikh**

- GitHub: https://github.com/Kaushar718
- LinkedIn: Add your LinkedIn profile URL here.

---

⭐ If you find this project useful, consider giving the repository a star.

**Built with Python and Django.**
