# Advanced Django Blogging Platform

A professional and scalable blogging platform built with Django, Django REST Framework, PostgreSQL, Redis, Celery, Docker, and Django Channels.

This project demonstrates modern backend engineering concepts including REST APIs, JWT authentication, asynchronous task processing, WebSockets, Docker containerization, Redis caching, and PostgreSQL database integration.

---

# Features

## Authentication System
- User Registration & Login
- JWT Authentication
- Password Reset System
- Email Verification
- Secure Authentication Flow
- Protected Routes & APIs

---

## Blog Features
- Create, Update & Delete Posts
- Categories & Tags
- Rich Text Content
- Blog Search Functionality
- Comment System
- Like & Bookmark System
- User Profiles
- Dynamic Content Management

---

## Real-Time Features
- Django Channels Integration
- WebSocket Notifications
- Real-Time Communication

---

## Async Task Management
- Celery Integration
- Celery Beat Scheduler
- Background Task Processing
- Redis Broker Support

---

## REST API Features
- Django REST Framework APIs
- JWT Protected APIs
- RESTful Architecture
- API Authentication & Authorization

---

# Tech Stack

## Backend
- Django
- Django REST Framework
- PostgreSQL
- Redis
- Celery
- Django Channels
- Daphne

---

## Frontend
- HTML5
- CSS3
- Bootstrap
- JavaScript

---

## DevOps & Tools
- Docker
- Docker Compose
- Git
- GitHub
- SQLite
- PostgreSQL

---

# Project Structure

```bash
accounts/
api/
blog/
core/
templates/
static/
media/
Dockerfile
docker-compose.yml
manage.py
requirements.txt
```

---

# Installation Guide

## 1. Clone Repository

```bash
git clone https://github.com/MuhammadHaseeb3112/Advanced-Django-Blogging-Platform.git

cd Advanced-Django-Blogging-Platform
```

---

## 2. Create Virtual Environment

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

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create a `.env` file in the root directory:

```env
SECRET_KEY=your_secret_key

DEBUG=True

POSTGRES_DB=django_blog
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

---

# Database Setup

## SQLite (Development)

```bash
python manage.py migrate
```

---

## PostgreSQL

Update PostgreSQL settings inside `.env` file.

Run migrations:

```bash
python manage.py migrate
```

---

# Run Development Server

```bash
python manage.py runserver
```

Visit:

```bash
http://127.0.0.1:8000/
```

---

# Docker Setup

## Build Containers

```bash
docker compose build
```

---

## Run Containers

```bash
docker compose up
```

---

## Run In Detached Mode

```bash
docker compose up -d
```

---

# Celery Setup

## Start Celery Worker

```bash
celery -A core worker -l info -P solo
```

---

## Start Celery Beat

```bash
celery -A core beat -l info
```

---

# WebSocket Server

Run Daphne server:

```bash
daphne core.asgi:application
```

---

# Future Improvements

- Docker Production Deployment
- CI/CD Pipeline
- AWS Deployment
- Nginx + Gunicorn Setup
- Elasticsearch Integration
- AI-Based Content Recommendations
- Advanced Analytics Dashboard
- Kubernetes Deployment

---

# Learning Objectives

This project demonstrates:

- Django Backend Development
- REST API Development
- Authentication Systems
- PostgreSQL Integration
- Redis Caching
- Docker Containerization
- Celery Background Tasks
- Real-Time WebSocket Communication
- Production-Level Project Structure

---

# Screenshots

Project screenshots will be added soon.

---

# Author

## Muhammad Haseeb

GitHub:
https://github.com/MuhammadHaseeb3112

---

# License

This project is licensed under the MIT License.

---
