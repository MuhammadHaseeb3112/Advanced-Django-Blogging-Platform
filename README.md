# Advanced Django Blogging Platform

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Django](https://img.shields.io/badge/Django-6.0-green)
![Django REST Framework](https://img.shields.io/badge/DRF-REST%20API-red)
![Docker](https://img.shields.io/badge/Docker-Enabled-blue)
![Redis](https://img.shields.io/badge/Redis-Caching-red)
![Celery](https://img.shields.io/badge/Celery-Background%20Tasks-green)
![WebSockets](https://img.shields.io/badge/WebSockets-Channels-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

A professional, scalable, and production-ready blogging platform built with **Django**, **Django REST Framework**, **PostgreSQL**, **Redis**, **Celery**, **Docker**, and **Django Channels**.

This project demonstrates modern backend engineering concepts including REST APIs, JWT authentication, asynchronous task processing, WebSockets, Docker containerization, Redis caching, PostgreSQL integration, and analytics dashboards.

---

# Live Features

## Authentication System

* User Registration
* User Login & Logout
* JWT Authentication
* Password Change
* Password Reset
* Email Verification
* Protected APIs
* Role-Based Permissions

---

## Blog Features

* Create Posts
* Update Posts
* Delete Posts
* Categories Management
* Tags Management
* Rich Content Publishing
* Draft & Published Posts
* Scheduled Publishing
* Blog Search
* User Profiles
* Author Profiles

---

## Engagement Features

* Comments System
* Like Posts
* Bookmark Posts
* Notification System
* Trending Posts
* Most Viewed Posts
* Featured Posts

---

## Analytics Dashboard

* Total Users
* Total Posts
* Total Categories
* Total Tags
* Total Views
* Total Comments
* Platform Likes
* Platform Bookmarks
* Author Analytics
* Dashboard Statistics
* Trending Content
* Top Categories

---

## Real-Time Features

* Django Channels
* WebSocket Integration
* Real-Time Notifications
* Live Updates

---

## Background Task Processing

* Celery Integration
* Celery Beat Scheduler
* Automated Tasks
* Background Processing
* Redis Broker Support

---

## REST API Features

* Django REST Framework
* JWT Protected APIs
* ViewSets
* Filtering
* Pagination
* Permissions
* OpenAPI Schema
* Swagger Documentation
* ReDoc Documentation

---

# Technology Stack

## Backend

* Python 3.12
* Django 6
* Django REST Framework
* PostgreSQL
* SQLite
* Redis
* Celery
* Django Channels
* Daphne

---

## Frontend

* HTML5
* CSS3
* Bootstrap
* JavaScript

---

## DevOps & Infrastructure

* Docker
* Docker Compose
* Nginx
* Git
* GitHub

---

# Architecture

Client Browser

↓

Django Templates

↓

Django Views & DRF APIs

↓

PostgreSQL Database

↓

Redis Cache / Broker

↓

Celery Workers

↓

Django Channels (WebSockets)

↓

Docker + Nginx

---

# Project Structure

```bash
accounts/
api/
│
├── filters/
├── pagination/
├── permissions/
├── serializers/
├── services/
└── views/
│
blog/
core/
nginx/
templates/
static/
media/

Dockerfile
docker-compose.yml
requirements.txt
manage.py
README.md
```

# Installation

## Clone Repository

```bash
git clone https://github.com/MuhammadHaseeb3112/Advanced-Django-Blogging-Platform.git

cd Advanced-Django-Blogging-Platform
```

## Create Virtual Environment

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

### Linux / Mac

```bash
python3 -m venv venv

source venv/bin/activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

# Environment Variables

Create a `.env` file:

```env
SECRET_KEY=your_secret_key

DEBUG=True

POSTGRES_DB=django_blog

POSTGRES_USER=postgres

POSTGRES_PASSWORD=your_password

POSTGRES_HOST=db

POSTGRES_PORT=5432
```

# Database Setup

## SQLite

```bash
python manage.py migrate
```

## PostgreSQL

Update PostgreSQL credentials in `.env`

Then:

```bash
python manage.py migrate
```

# Run Development Server

```bash
python manage.py runserver
```

Open:

```bash
http://127.0.0.1:8000/
```

# Docker Setup

## Build Containers

```bash
docker compose build
```

## Start Containers

```bash
docker compose up
```

## Detached Mode

```bash
docker compose up -d
```

## Stop Containers

```bash
docker compose down
```

# Celery Setup

## Start Celery Worker

```bash
celery -A core worker -l info
```

## Start Celery Beat

```bash
celery -A core beat -l info
```

# WebSocket Server

```bash
daphne core.asgi:application
```

# API Documentation

## Swagger UI

```text
http://localhost/api/docs/
```

## ReDoc

```text
http://localhost/api/redoc/
```

## OpenAPI Schema

```text
http://localhost/api/schema/
```

# Screenshots

Create an assets folder:

```text
assets/
├── home.png
├── dashboard.png
├── swagger.png
├── redoc.png
```

## Home Page

```markdown
![Home](assets/home.png)
```

## Dashboard

```markdown
![Dashboard](assets/dashboard.png)
```

## Swagger Documentation

```markdown
![Swagger](assets/swagger.png)
```

## ReDoc Documentation

```markdown
![ReDoc](assets/redoc.png)
```

# Highlights

This project demonstrates:

* Advanced Django Development
* Django REST Framework
* JWT Authentication
* PostgreSQL Integration
* Redis Caching
* Celery Background Tasks
* WebSocket Communication
* Docker Containerization
* Nginx Reverse Proxy
* API Documentation
* Clean Architecture
* Production-Oriented Design

# Future Improvements

* CI/CD Pipeline
* GitHub Actions
* AWS Deployment
* Kubernetes Deployment
* Elasticsearch Integration
* AI Content Recommendations
* Social Authentication
* Two-Factor Authentication
* Advanced Monitoring
* Multi-Tenant Blogging

# Release Information

Current Stable Release:

```text
v1.0.0
```

Repository:

https://github.com/MuhammadHaseeb3112/Advanced-Django-Blogging-Platform

# Author

## Muhammad Haseeb

GitHub:

https://github.com/MuhammadHaseeb3112

# License

This project is licensed under the MIT License.

© 2026 Muhammad Haseeb. All rights reserved.
