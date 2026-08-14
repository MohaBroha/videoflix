# 🎬 Videoflix Backend

Videoflix is a Django REST Framework backend for a video streaming platform.

The backend provides:

- User registration and authentication
- JWT-based authentication
- Django Admin for video management
- PostgreSQL database
- Redis
- Django RQ background jobs
- FFmpeg video processing
- HLS streaming
- 480p, 720p and 1080p video output
- Docker-based development environment
- WhiteNoise static file handling
- CORS support for the provided frontend

Videos are uploaded through the Django Admin Panel. After a video is created, a background job processes the source video with FFmpeg and generates HLS playlists and video segments for multiple resolutions.

---

# 📑 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Installation](#installation)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Open the Backend Directory](#2-open-the-backend-directory)
  - [3. Configure Environment Variables](#3-configure-environment-variables)
  - [4. Start Docker](#4-start-docker)
  - [5. Build and Start the Application](#5-build-and-start-the-application)
  - [6. Apply Database Migrations](#6-apply-database-migrations)
  - [7. Create a Superuser](#7-create-a-superuser)
  - [8. Verify Django](#8-verify-django)
  - [9. Install FFmpeg](#9-install-ffmpeg)
  - [10. Start the Frontend](#10-start-the-frontend)
- [Environment Variables](#environment-variables)
- [Docker Services](#docker-services)
- [Database](#database)
- [Redis and Django RQ](#redis-and-django-rq)
- [FFmpeg and Video Processing](#ffmpeg-and-video-processing)
- [Django Admin](#django-admin)
- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
- [HLS Streaming](#hls-streaming)
- [Frontend Integration](#frontend-integration)
- [Static and Media Files](#static-and-media-files)
- [Testing](#testing)
- [Generated Files](#generated-files)
- [Troubleshooting](#troubleshooting)
- [Development Workflow](#development-workflow)

---

# Overview

Videoflix is a video streaming application built with Django and Django REST Framework.

The backend combines:

- Django
- Django REST Framework
- PostgreSQL
- Redis
- Django RQ
- FFmpeg
- HLS
- JWT authentication
- Docker Compose

Videos are uploaded through Django Admin.

After the upload is saved, a Django `post_save` signal creates a background processing job. Django RQ uses Redis as its queue backend. The job calls FFmpeg and generates HLS output for:

- 480p
- 720p
- 1080p

The generated HLS playlists and video segments are served through authenticated API endpoints.

---

# Features

## Authentication

- User registration
- User login
- User logout
- JWT authentication
- Access tokens
- Refresh tokens
- JWT token blacklist
- Cookie-based JWT authentication
- Protected API endpoints
- Account activation
- Password reset flow

## Video Management

- Video management through Django Admin
- Video upload through Django Admin
- Video metadata
- Video thumbnail support
- Automatic video processing after upload

## Background Processing

- Redis integration
- Django RQ integration
- Background processing
- Queued video conversion
- FFmpeg conversion

## Video Streaming

- HLS video generation
- HLS playlist delivery
- HLS segment delivery
- 480p output
- 720p output
- 1080p output
- `.m3u8` playlists
- `.ts` video segments
- Authenticated streaming endpoints

## Database

- PostgreSQL
- Django migrations
- Persistent Docker volume

## Development

- Docker Compose
- Gunicorn
- WhiteNoise
- CORS support
- Environment-based configuration

---

# Tech Stack

## Backend

- Python 3.14
- Django 5.2
- Django REST Framework

## Authentication

- djangorestframework-simplejwt
- JWT access tokens
- JWT refresh tokens
- Token blacklist
- Custom Cookie JWT authentication

## Database

- PostgreSQL
- psycopg2-binary

## Queue and Cache

- Redis
- Django RQ
- RQ
- django-redis

## Video Processing

- FFmpeg
- HLS
- Pillow

## Configuration

- python-dotenv
- Environment variables

## Infrastructure

- Docker
- Docker Compose
- Gunicorn
- WhiteNoise

---

# Architecture

The current development setup runs the backend inside Docker Compose.

The main services are:

```text
┌─────────────────────────────────────────────┐
│              Docker Compose                 │
│                                             │
│  ┌───────────────────────────────────────┐  │
│  │ web                                   │  │
│  │ Django + Gunicorn                     │  │
│  │                                       │  │
│  │ http://127.0.0.1:8000                 │  │
│  └───────────────┬───────────────────────┘  │
│                  │                          │
│        ┌─────────┴─────────┐                │
│        │                   │                │
│        ▼                   ▼                │
│  ┌───────────┐       ┌───────────┐          │
│  │ PostgreSQL│       │   Redis   │          │
│  │    db     │       │   redis   │          │
│  └───────────┘       └───────────┘          │
│                                             │
└─────────────────────────────────────────────┘
```

The frontend is served separately during local development.

The frontend communicates with:

```text
http://127.0.0.1:8000/api/
```

The application therefore consists of:

```text
Frontend
   │
   │ HTTP / JSON / HLS
   ▼
Django + DRF
   │
   ├──────────────► PostgreSQL
   │
   └──────────────► Redis / Django RQ
                         │
                         ▼
                       FFmpeg
                         │
                         ▼
                    HLS output
```

---

# Video Processing Architecture

The complete processing workflow is:

```text
Django Admin
     │
     ▼
Video Upload
     │
     ▼
Video saved
     │
     ▼
post_save signal
     │
     ▼
Django RQ
     │
     ▼
process_video()
     │
     ▼
FFmpeg
     │
     ├────────► 480p
     │
     ├────────► 720p
     │
     └────────► 1080p
                  │
                  ▼
             HLS Generation
                  │
                  ├── index.m3u8
                  │
                  └── index0.ts
                         │
                         ▼
                   Streaming API
                         │
                         ▼
                     Frontend
```

The video processing code is located in:

```text
videos/functions.py
```

The background job is located in:

```text
videos/tasks.py
```

---

# Project Structure

```text
videoflix/
│
├── backend/
│   │
│   ├── accounts/
│   │   ├── api/
│   │   │   ├── authentication.py
│   │   │   ├── serializers.py
│   │   │   ├── urls.py
│   │   │   └── views.py
│   │   ├── migrations/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   └── ...
│   │
│   ├── videos/
│   │   ├── api/
│   │   │   ├── serializers.py
│   │   │   ├── urls.py
│   │   │   └── views.py
│   │   ├── migrations/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── functions.py
│   │   ├── models.py
│   │   ├── tasks.py
│   │   └── ...
│   │
│   ├── core/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   │
│   ├── media/
│   ├── static/
│   │
│   ├── .env
│   ├── .env.template
│   ├── .gitignore
│   ├── docker-compose.yml
│   ├── Dockerfile
│   ├── manage.py
│   ├── README.md
│   └── requirements.txt
│
└── frontend/
    ├── pages/
    ├── shared/
    ├── assets/
    └── ...
```

Generated media and HLS files should not be committed to Git.

---

# Requirements

Before running the project, install:

- Git
- Python 3.14
- Docker Desktop
- Docker Compose
- FFmpeg

Check Python:

```powershell
python --version
```

Check Docker:

```powershell
docker --version
docker compose version
```

Check FFmpeg:

```powershell
ffmpeg -version
```

---

# Installation

## 1. Clone the Repository

Clone the project:

```bash
git clone <YOUR_REPOSITORY_URL>
```

Enter the project:

```bash
cd videoflix
```

---

## 2. Open the Backend Directory

```bash
cd backend
```

All backend commands should be executed from this directory unless stated otherwise.

---

## 3. Configure Environment Variables

Create the local environment file from the example:

### Windows PowerShell

```powershell
Copy-Item .env.template .env
```

### Linux / macOS

```bash
cp .env.template .env
```

The real `.env` file contains local configuration and secrets.

It must not be committed to Git.

The `.env.template` file contains placeholders and should be committed.

---

# Environment Variables

The backend uses environment variables for configuration.

The important variables are:

```env
SECRET_KEY=your-secret-key
DEBUG=True

DB_NAME=videoflix_db
DB_USER=videoflix_user
DB_PASSWORD=your-secure-password
DB_HOST=db
DB_PORT=5432

REDIS_LOCATION=redis://redis:6379/1

ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:5500,http://127.0.0.1:5500
```

The values above are examples.

Do not commit real secrets.

The Django settings load the `.env` file with `python-dotenv`.

---

# 4. Start Docker

Make sure Docker Desktop is running.

Check:

```powershell
docker ps
```

---

# 5. Build and Start the Application

Build the backend image and start all services:

```powershell
docker compose up --build -d
```

Check the services:

```powershell
docker compose ps
```

The application should contain the following services:

```text
web
db
redis
```

The backend is exposed on:

```text
http://127.0.0.1:8000/
```

The API is available under:

```text
http://127.0.0.1:8000/api/
```

---

# Docker Services

## Web

The `web` service runs the Django backend using Gunicorn.

It is exposed on:

```text
127.0.0.1:8000
```

## PostgreSQL

PostgreSQL is used as the application database.

The Docker service is:

```text
db
```

## Redis

Redis is used by:

- Django RQ
- Background processing
- Django cache

The Docker service is:

```text
redis
```

---

# Useful Docker Commands

Start the application:

```powershell
docker compose up -d
```

Rebuild the application:

```powershell
docker compose up --build -d
```

Stop the application:

```powershell
docker compose down
```

Check services:

```powershell
docker compose ps
```

View backend logs:

```powershell
docker compose logs web
```

Follow backend logs:

```powershell
docker compose logs -f web
```

View the last 100 lines:

```powershell
docker compose logs web --tail=100
```

Open a shell inside the backend container:

```powershell
docker compose exec web bash
```

---

# 6. Apply Database Migrations

Run:

```powershell
docker compose exec web python manage.py migrate
```

This creates the required Django database tables.

Check migrations:

```powershell
docker compose exec web python manage.py showmigrations
```

---

# 7. Create a Superuser

Create a Django administrator:

```powershell
docker compose exec web python manage.py createsuperuser
```

Follow the prompts.

The superuser is required to access:

```text
http://127.0.0.1:8000/admin/
```

A normal Videoflix user account is not automatically a Django Admin user.

---

# 8. Verify Django

Run:

```powershell
docker compose exec web python manage.py check
```

Expected result:

```text
System check identified no issues (0 silenced).
```

---

# 9. Install FFmpeg

FFmpeg is not installed through `requirements.txt`.

It must be available to the environment where the video processing job runs.

Check:

```powershell
ffmpeg -version
```

If FFmpeg is unavailable, install it and make sure its `bin` directory is available through `PATH`.

---

# 10. Start the Frontend

The Academy frontend is a separate static frontend.

Start the frontend with a local static server.

The frontend API configuration points to:

```javascript
const API_BASE_URL = 'http://127.0.0.1:8000/api/';
```

The frontend therefore communicates with the Dockerized backend.

The frontend must be opened through its local web server rather than directly through the filesystem.

Example:

```text
http://127.0.0.1:5500/
```

---

# Django Admin

Open:

```text
http://127.0.0.1:8000/admin/
```

Login using the Django superuser.

The Django Admin is used to:

- create videos
- upload video files
- edit video metadata
- manage users
- manage application data

After saving a video, the background processing pipeline starts automatically.

---

# Video Processing

Videos are uploaded through Django Admin.

After the model is saved, the `post_save` signal triggers the background task.

The task calls:

```text
videos.tasks.process_video()
```

The actual FFmpeg conversion is implemented in:

```text
videos.functions.convert_video()
```

The supported resolutions are:

```text
480p
720p
1080p
```

For a video with ID `1`, the generated structure is:

```text
media/
└── hls/
    └── 1/
        ├── 480p/
        │   ├── index.m3u8
        │   └── index0.ts
        │
        ├── 720p/
        │   ├── index.m3u8
        │   └── index0.ts
        │
        └── 1080p/
            ├── index.m3u8
            └── index0.ts
```

Longer videos may contain multiple `.ts` segment files.

---

# Redis and Django RQ

Redis is used as the queue backend for Django RQ.

The default queue is:

```text
default
```

The configured default timeout is:

```text
900 seconds
```

The processing task is:

```text
videos/tasks.py
```

The FFmpeg logic is:

```text
videos/functions.py
```

The workflow is:

```text
Video
  ↓
post_save
  ↓
RQ job
  ↓
Redis
  ↓
process_video()
  ↓
FFmpeg
  ↓
HLS
```

---

# Authentication

Videoflix uses JWT authentication.

The project uses a custom authentication class:

```text
accounts.api.authentication.CookieJWTAuthentication
```

Authentication supports:

- Access tokens
- Refresh tokens
- Token blacklist
- Cookie-based authentication

Configured token lifetimes:

```text
Access token: 30 minutes
Refresh token: 7 days
```

---

# API Endpoints

## Register

```http
POST /api/register/
```

Creates a new user account.

Example request:

```json
{
    "email": "user@example.com",
    "password": "test12345",
    "confirmed_password": "test12345",
    "privacy_policy": "on"
}
```

---

## Login

```http
POST /api/login/
```

Authenticates a user.

The frontend uses this endpoint for login.

---

## Logout

```http
POST /api/logout/
```

Logs out the authenticated user.

---

## Refresh Token

```http
POST /api/token/refresh/
```

Refreshes authentication using the configured JWT refresh flow.

---

## Get Videos

```http
GET /api/video/
```

Returns the available videos.

Authentication is required.

---

## Get HLS Manifest

```http
GET /api/video/<movie_id>/<resolution>/index.m3u8
```

Example:

```http
GET /api/video/1/480p/index.m3u8
```

Supported resolutions:

```text
480p
720p
1080p
```

Authentication is required.

Expected response:

```text
200 OK
```

Content type:

```text
application/vnd.apple.mpegurl
```

---

## Get HLS Segment

```http
GET /api/video/<movie_id>/<resolution>/<segment>/
```

Example:

```http
GET /api/video/1/480p/index0.ts
```

Expected response:

```text
200 OK
```

Content type:

```text
video/MP2T
```

Authentication is required.

---

# HLS Streaming

HLS streaming works by requesting a playlist first.

Example:

```http
GET /api/video/1/480p/index.m3u8
```

The playlist references one or more `.ts` video segments.

For example:

```text
index0.ts
```

The client then requests:

```http
GET /api/video/1/480p/index0.ts
```

The video player continues requesting segments during playback.

This allows the frontend to stream the video instead of downloading the complete source video before playback starts.

---

# Frontend Integration

The Academy frontend is used as the client for the backend.

The frontend API configuration is:

```javascript
const API_BASE_URL = 'http://127.0.0.1:8000/api/';
```

Relevant frontend endpoints include:

```javascript
const LOGIN_URL = 'login/';
const REGISTER_URL = 'register/';
const FORGET_PASSWORD_URL = 'password_reset/';
const REFRESH_URL = 'token/refresh/';
```

The frontend also constructs HLS URLs for individual videos and resolutions.

The frontend must be served through a local HTTP server.

Example:

```text
http://127.0.0.1:5500/
```

Do not open the HTML files directly using `file://`.

---

# CORS

The backend allows requests from the local frontend development server.

Example origins:

```text
http://127.0.0.1:5500
http://localhost:5500
```

Credentials are enabled because authentication uses cookies.

```python
CORS_ALLOW_CREDENTIALS = True
```

If the frontend runs on another origin, that origin must be added to the backend CORS configuration.

---

# Static and Media Files

Static files are configured with:

```python
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"
```

Media files are configured with:

```python
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
```

WhiteNoise is used for static file handling.

The backend therefore includes:

```text
whitenoise
```

in its Python dependencies.

Static files can be collected with:

```powershell
docker compose exec web python manage.py collectstatic --noinput
```

---

# Testing

## Django System Check

Run:

```powershell
docker compose exec web python manage.py check
```

Expected:

```text
System check identified no issues (0 silenced).
```

---

## Django Tests

Run:

```powershell
docker compose exec web python manage.py test
```

If no test modules have been created yet, Django may report:

```text
Found 0 test(s).
```

This means no tests were discovered; it is not itself a failing test.

---

# API Testing with Postman

A recommended testing sequence is:

```text
1. Register
       ↓
2. Login
       ↓
3. Obtain authentication
       ↓
4. Request video list
       ↓
5. Request HLS manifest
       ↓
6. Request HLS segment
       ↓
7. Test invalid requests
```

For authenticated API requests, use the access token.

Example:

```text
Authorization
→ Bearer Token
→ <ACCESS_TOKEN>
```

---

# HLS Testing

## Manifest Success

```http
GET /api/video/1/480p/index.m3u8
```

Expected:

```text
200 OK
```

---

## Manifest 404

Request a non-existing video or resolution.

Expected:

```text
404 Not Found
```

---

## Segment Success

```http
GET /api/video/1/480p/index0.ts
```

Expected:

```text
200 OK
```

---

## Segment 404

```http
GET /api/video/1/480p/fake.ts
```

Expected:

```text
404 Not Found
```

---

# Generated Files

Generated files should not be committed to Git.

The `.gitignore` should exclude:

```gitignore
.env
.venv/
venv/

__pycache__/
*.py[cod]

*.log

media/
static/

hls/
thumbnails/

*.mp4

.vscode/
.idea/

.DS_Store
Thumbs.db
```

The real `.env` file must never be committed.

The `.env.template` file should be committed.

---

# Troubleshooting

## Pillow is not installed

If Django reports:

```text
Cannot use ImageField because Pillow is not installed.
```

Install Pillow:

```powershell
python -m pip install Pillow
```

Then verify:

```powershell
python -m pip show Pillow
```

For Docker, rebuild the image:

```powershell
docker compose up --build -d
```

---

## Docker container does not start

Check:

```powershell
docker compose ps
```

Then inspect the backend:

```powershell
docker compose logs web
```

If the Docker image has changed, rebuild:

```powershell
docker compose up --build -d
```

---

## `backend.entrypoint.sh: no such file or directory`

This usually indicates that the Docker image cannot find or execute the configured entrypoint.

Check:

- the file exists
- the path in the Dockerfile is correct
- the file has the correct line endings
- the image is rebuilt after changes

Then:

```powershell
docker compose build web
docker compose up -d
```

---

## PostgreSQL connection error

Check:

```powershell
docker compose ps
```

Make sure the database container is running.

Then:

```powershell
docker compose logs db
```

---

## Redis connection error

Check:

```powershell
docker compose ps
```

Then:

```powershell
docker compose logs redis
```

---

## Static files return 404

Run:

```powershell
docker compose exec web python manage.py collectstatic --noinput
```

Then rebuild/restart if necessary:

```powershell
docker compose up --build -d
```

Check the backend logs:

```powershell
docker compose logs web
```

---

## Video does not appear

Check:

```text
1. User is logged in
2. Video exists in Django Admin
3. GET /api/video/ works
4. Video processing completed
5. HLS files exist
```

Check generated HLS files:

```powershell
docker compose exec web ls -R /app/media/hls
```

A processed video should contain:

```text
480p/
720p/
1080p/
```

---

## HLS manifest returns 404

Check:

```text
1. The video exists.
2. The video has been processed.
3. The requested resolution exists.
4. index.m3u8 exists.
```

Example:

```text
media/
└── hls/
    └── 1/
        └── 480p/
            └── index.m3u8
```

Also verify the API URL:

```text
/api/video/1/480p/index.m3u8
```

---

## HLS segment returns 404

Check the generated directory:

```text
media/
└── hls/
    └── 1/
        └── 480p/
            ├── index.m3u8
            └── index0.ts
```

Request the exact segment filename.

---

## Video processing does not start

Check the backend logs:

```powershell
docker compose logs -f web
```

Look for:

```text
RQ
process_video
FFmpeg
```

Also check that Redis is running:

```powershell
docker compose ps
```

---

## FFmpeg not found

Run:

```powershell
ffmpeg -version
```

If the command is not recognized, install FFmpeg and add its `bin` directory to the system `PATH`.

Restart PowerShell after changing the PATH.

---

# Development Workflow

A clean development workflow is:

```text
Start Docker
      ↓
PostgreSQL + Redis
      ↓
Start / rebuild web container
      ↓
Django available on port 8000
      ↓
Start Academy frontend
      ↓
Login / register
      ↓
Upload test video through Admin
      ↓
RQ job
      ↓
FFmpeg
      ↓
HLS generation
      ↓
Test frontend playback
      ↓
python manage.py check
      ↓
python manage.py test
      ↓
git status
      ↓
git add
      ↓
git commit
      ↓
git push
```

Useful commands:

```powershell
docker compose up -d
```

```powershell
docker compose up --build -d
```

```powershell
docker compose ps
```

```powershell
docker compose logs web --tail=100
```

```powershell
docker compose exec web python manage.py check
```

```powershell
docker compose exec web python manage.py test
```

```powershell
git status
```

---

# Clean Setup from Scratch

For a new developer:

```powershell
git clone <YOUR_REPOSITORY_URL>

cd videoflix

cd backend

Copy-Item .env.template .env
```

Configure `.env`.

Then:

```powershell
docker compose up --build -d
```

Apply migrations:

```powershell
docker compose exec web python manage.py migrate
```

Create the admin user:

```powershell
docker compose exec web python manage.py createsuperuser
```

Check Django:

```powershell
docker compose exec web python manage.py check
```

Check services:

```powershell
docker compose ps
```

Start the Academy frontend separately with its local static server.

Open:

```text
http://127.0.0.1:5500/
```

Django Admin:

```text
http://127.0.0.1:8000/admin/
```

API:

```text
http://127.0.0.1:8000/api/
```

---

# Final System Overview

The finished Videoflix system works as follows:

```text
                    ┌──────────────────┐
                    │ Academy Frontend │
                    │ localhost:5500   │
                    └────────┬─────────┘
                             │
                             │ HTTP / JSON / HLS
                             ▼
                  ┌─────────────────────┐
                  │ Django + DRF       │
                  │ Gunicorn / Docker  │
                  │ :8000              │
                  └──────┬──────┬──────┘
                         │      │
              ┌──────────┘      └──────────┐
              ▼                            ▼
      ┌──────────────┐              ┌──────────────┐
      │ PostgreSQL   │              │ Redis        │
      │              │              │              │
      │ Users        │              │ Django RQ    │
      │ Videos       │              │ Queue        │
      └──────────────┘              └──────┬───────┘
                                           │
                                           ▼
                                    ┌──────────────┐
                                    │ FFmpeg       │
                                    │              │
                                    │ 480p         │
                                    │ 720p         │
                                    │ 1080p        │
                                    └──────┬───────┘
                                           │
                                           ▼
                                    ┌──────────────┐
                                    │ HLS          │
                                    │              │
                                    │ index.m3u8   │
                                    │ index0.ts    │
                                    └──────┬───────┘
                                           │
                                           ▼
                                    Streaming API
                                           │
                                           ▼
                                    Academy Frontend
```

---

# Author

**Moha Broha**

Fullstack Developer in Training