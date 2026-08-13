# 🎬 Videoflix Backend

Videoflix is a Django REST Framework backend for a video streaming platform.

The backend provides user authentication, video management, background video processing and authenticated HLS video streaming.

Videos are uploaded through the Django Admin Panel. After an upload, the video processing workflow is triggered and the video is converted with FFmpeg into multiple HLS resolutions. Redis and Django RQ are used for background job handling, while PostgreSQL is used as the application database.

---

## 📑 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Installation](#installation)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Open the Backend Directory](#2-open-the-backend-directory)
  - [3. Create a Virtual Environment](#3-create-a-virtual-environment)
  - [4. Activate the Virtual Environment](#4-activate-the-virtual-environment)
  - [5. Install Python Dependencies](#5-install-python-dependencies)
  - [6. Configure Environment Variables](#6-configure-environment-variables)
  - [7. Install and Start Docker Desktop](#7-install-and-start-docker-desktop)
  - [8. Start PostgreSQL and Redis](#8-start-postgresql-and-redis)
  - [9. Apply Database Migrations](#9-apply-database-migrations)
  - [10. Create a Superuser](#10-create-a-superuser)
  - [11. Install FFmpeg](#11-install-ffmpeg)
  - [12. Start Django](#12-start-django)
  - [13. Start the RQ Worker](#13-start-the-rq-worker)
- [Environment Variables](#environment-variables)
- [Docker Services](#docker-services)
- [Database](#database)
- [Redis and Django RQ](#redis-and-django-rq)
- [FFmpeg and Video Processing](#ffmpeg-and-video-processing)
- [Django Admin](#django-admin)
- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
  - [Register](#register)
  - [Login](#login)
  - [Logout](#logout)
  - [Refresh Token](#refresh-token)
  - [Get Videos](#get-videos)
  - [Get HLS Manifest](#get-hls-manifest)
  - [Get HLS Segment](#get-hls-segment)
- [HLS Streaming](#hls-streaming)
- [Testing with Postman](#testing-with-postman)
- [Testing the HLS Endpoints](#testing-the-hls-endpoints)
- [Django Checks and Tests](#django-checks-and-tests)
- [Generated Files](#generated-files)
- [Troubleshooting](#troubleshooting)
- [Clean Setup from Scratch](#clean-setup-from-scratch)
- [Development Workflow](#development-workflow)
- [Author](#author)

---

## Overview

Videoflix is a backend application for a video streaming platform built with Django and Django REST Framework.

The application combines several backend technologies:

- Django REST Framework provides the REST API.
- PostgreSQL stores application data.
- Redis provides the queue backend.
- Django RQ handles background jobs.
- FFmpeg processes uploaded videos.
- HLS is used to provide streamable video content.
- JWT is used to protect authenticated API endpoints.

Videos are not uploaded through a public REST endpoint. Video management and uploads are handled through the Django Admin Panel.

After a video is uploaded and saved, the application queues a background processing job. FFmpeg converts the source video into HLS output for multiple resolutions.

The generated playlists and video segments can then be requested through authenticated API endpoints.

---

## Features

### Authentication

- User registration
- User login
- User logout
- JWT authentication
- Access tokens
- Refresh tokens
- JWT token blacklist support
- Protected API endpoints
- Custom JWT authentication

### Video Management

- Video management through Django Admin
- Video upload through Django Admin
- Video metadata storage
- Automatic processing after video creation

### Background Processing

- Redis integration
- Django RQ integration
- Background video processing
- Queued processing jobs
- FFmpeg conversion

### Video Streaming

- HLS video generation
- HLS playlist delivery
- HLS segment delivery
- 480p output
- 720p output
- 1080p output
- `.m3u8` playlists
- `.ts` video segments
- Authenticated streaming endpoints

### Database

- PostgreSQL database
- Django migrations
- Persistent PostgreSQL Docker volume

---

## Tech Stack

### Backend

- Python 3.14
- Django 5.2
- Django REST Framework

### Authentication

- djangorestframework-simplejwt
- JWT access tokens
- JWT refresh tokens
- Token blacklist

### Database

- PostgreSQL 17
- psycopg2

### Queue and Cache

- Redis 7
- Django RQ
- RQ
- django-redis

### Video Processing

- FFmpeg
- HLS

### Configuration

- python-dotenv
- Environment variables

### Infrastructure

- Docker Desktop
- Docker Compose

---

## Architecture

The local development environment uses a hybrid setup.

Django runs directly on the host system inside a Python virtual environment.

PostgreSQL and Redis run inside Docker containers.

```text
┌──────────────────────────────────────┐
│          Local Development           │
│                                      │
│  Python Virtual Environment          │
│                                      │
│  ┌───────────────────────────────┐   │
│  │ Django / DRF                  │   │
│  │ http://127.0.0.1:8000        │   │
│  └──────────────┬────────────────┘   │
│                 │                    │
└─────────────────┼────────────────────┘
                  │
          localhost ports
                  │
       ┌──────────┴──────────┐
       │                     │
       ▼                     ▼
┌──────────────┐      ┌──────────────┐
│ PostgreSQL   │      │ Redis        │
│ Docker       │      │ Docker       │
│ Port 5432    │      │ Port 6379    │
└──────────────┘      └──────────────┘
```

Because Django runs outside Docker, the local Django configuration uses:

```env
POSTGRES_HOST=localhost
REDIS_URL=redis://localhost:6379/1
```

The Docker service names `db` and `redis` would only be used as hostnames by applications running inside the same Docker Compose network.

---

## Video Processing Architecture

The video processing workflow is:

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
post_save
     │
     ▼
Django RQ Queue
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
             ┌──────┴──────┐
             │             │
             ▼             ▼
        index.m3u8      index0.ts
             │             │
             └──────┬──────┘
                    │
                    ▼
             Streaming API
```

---

## Project Structure

```text
videoflix/
│
└── backend/
    │
    ├── accounts/
    │   ├── api/
    │   │   └── authentication.py
    │   │
    │   ├── migrations/
    │   ├── admin.py
    │   ├── apps.py
    │   ├── models.py
    │   └── ...
    │
    ├── videos/
    │   ├── api/
    │   │   ├── serializers.py
    │   │   ├── urls.py
    │   │   └── views.py
    │   │
    │   ├── migrations/
    │   ├── admin.py
    │   ├── apps.py
    │   ├── functions.py
    │   ├── models.py
    │   ├── tasks.py
    │   └── ...
    │
    ├── core/
    │   ├── settings.py
    │   ├── urls.py
    │   ├── asgi.py
    │   └── wsgi.py
    │
    ├── hls/
    ├── media/
    ├── static/
    ├── thumbnails/
    │
    ├── .env
    ├── .env.example
    ├── .gitignore
    ├── docker-compose.yml
    ├── Dockerfile
    ├── manage.py
    ├── README.md
    └── requirements.txt
```

> The current Dockerfile is not used for the local development setup. Django runs locally in the Python virtual environment, while PostgreSQL and Redis run through Docker Compose.

---

## Requirements

Before cloning and running the project, install the following software.

### Required Software

- Git
- Python 3.14 or newer
- pip
- Docker Desktop
- Docker Compose
- FFmpeg

### Check Git

```bash
git --version
```

### Check Python

```bash
python --version
```

On Linux or macOS you may need:

```bash
python3 --version
```

### Check pip

```bash
pip --version
```

### Check Docker

```bash
docker --version
```

### Check Docker Compose

```bash
docker compose version
```

### Check FFmpeg

```bash
ffmpeg -version
```

All required software should be available before continuing with the installation.

---

# Installation

## 1. Clone the Repository

Clone the repository:

```bash
git clone <YOUR_REPOSITORY_URL>
```

Enter the cloned project:

```bash
cd videoflix
```

---

## 2. Open the Backend Directory

Enter the Django backend:

```bash
cd backend
```

All commands in the following installation steps should be executed from the `backend` directory unless stated otherwise.

---

## 3. Create a Virtual Environment

A Python virtual environment keeps the project dependencies isolated from the global Python installation.

### Windows PowerShell / CMD

```powershell
python -m venv venv
```

### Linux / macOS

```bash
python3 -m venv venv
```

A new directory called `venv` will be created.

---

## 4. Activate the Virtual Environment

### Windows PowerShell

```powershell
venv\Scripts\activate
```

### Windows CMD

```cmd
venv\Scripts\activate.bat
```

### Linux / macOS

```bash
source venv/bin/activate
```

After activation, the terminal should show `(venv)`.

Example:

```text
(venv) PS C:\...\videoflix\backend>
```

The virtual environment must be activated whenever Django commands are executed.

---

## 5. Install Python Dependencies

Install all dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

After installation, verify that Django can load the project:

```bash
python manage.py check
```

At this stage, database-related operations may still require PostgreSQL to be started first.

---

## 6. Configure Environment Variables

The repository contains:

```text
.env.example
```

The real `.env` file is intentionally not committed because it contains environment-specific configuration and secrets.

Create `.env` from `.env.example`.

### Windows PowerShell

```powershell
Copy-Item .env.example .env
```

### Windows CMD

```cmd
copy .env.example .env
```

### Linux / macOS

```bash
cp .env.example .env
```

Open `.env`.

For the current local development architecture it should use:

```env
POSTGRES_DB=videoflix
POSTGRES_USER=videoflix
POSTGRES_PASSWORD=your-secure-password

POSTGRES_HOST=localhost
POSTGRES_PORT=5432

REDIS_URL=redis://localhost:6379/1

SECRET_KEY=your-django-secret-key
DEBUG=True
```

### POSTGRES_DB

```env
POSTGRES_DB=videoflix
```

Defines the PostgreSQL database name.

### POSTGRES_USER

```env
POSTGRES_USER=videoflix
```

Defines the PostgreSQL user.

### POSTGRES_PASSWORD

```env
POSTGRES_PASSWORD=your-secure-password
```

Choose your own password.

Docker Compose uses this value when creating PostgreSQL and Django uses the same value when connecting to PostgreSQL.

### POSTGRES_HOST

Because Django runs locally and PostgreSQL exposes port `5432` from Docker:

```env
POSTGRES_HOST=localhost
```

### POSTGRES_PORT

```env
POSTGRES_PORT=5432
```

### REDIS_URL

Because Django runs locally and Redis exposes port `6379` from Docker:

```env
REDIS_URL=redis://localhost:6379/1
```

### SECRET_KEY

Set a private Django secret key:

```env
SECRET_KEY=your-django-secret-key
```

Do not use the example value in production.

### DEBUG

For local development:

```env
DEBUG=True
```

### Important Security Note

Never commit the real `.env` file.

Only `.env.example` should be committed.

---

## 7. Install and Start Docker Desktop

PostgreSQL and Redis run through Docker Compose.

Start Docker Desktop before continuing.

Verify that Docker is running:

```bash
docker ps
```

If Docker is working, the command should execute without a connection error.

---

## 8. Start PostgreSQL and Redis

The project contains a `docker-compose.yml`.

It defines two services:

```text
db
redis
```

Start the services:

```bash
docker compose up -d
```

The `-d` option starts the containers in the background.

Check the containers:

```bash
docker ps
```

You should see:

```text
videoflix_db
videoflix_redis
```

### PostgreSQL

PostgreSQL is exposed on:

```text
localhost:5432
```

### Redis

Redis is exposed on:

```text
localhost:6379
```

### Check Docker Compose Status

```bash
docker compose ps
```

### Stop the Services

```bash
docker compose down
```

### Start the Services Again

```bash
docker compose up -d
```

### Important

Do not use:

```bash
docker compose down -v
```

unless you intentionally want to delete the PostgreSQL and Redis volumes.

The `-v` option removes the persistent volumes and therefore deletes stored local database data.

---

## 9. Apply Database Migrations

After PostgreSQL is running:

```bash
python manage.py migrate
```

This creates the required database tables.

The project includes Django migrations for applications including:

- accounts
- admin
- auth
- contenttypes
- django_rq
- sessions
- token_blacklist
- videos

After migrations, run:

```bash
python manage.py check
```

Expected output:

```text
System check identified no issues (0 silenced).
```

---

## 10. Create a Superuser

Create an administrator account:

```bash
python manage.py createsuperuser
```

Follow the prompts.

The superuser is required to access Django Admin and upload/manage videos.

---

## 11. Install FFmpeg

FFmpeg is not a Python package and is therefore not installed through `requirements.txt`.

It must be installed separately on the operating system.

### Windows

Install FFmpeg and add its `bin` directory to the Windows PATH environment variable.

After installation, close and reopen the terminal.

Verify:

```powershell
ffmpeg -version
```

The command must print FFmpeg version information.

If PowerShell reports that `ffmpeg` is not recognized, FFmpeg is either not installed or its `bin` directory is missing from PATH.

### Ubuntu / Debian

```bash
sudo apt update
sudo apt install ffmpeg
```

Verify:

```bash
ffmpeg -version
```

### macOS

If Homebrew is installed:

```bash
brew install ffmpeg
```

Verify:

```bash
ffmpeg -version
```

FFmpeg must be available before uploaded videos can be processed.

---

## 12. Start Django

Make sure:

- the virtual environment is activated
- `.env` exists
- Docker Desktop is running
- PostgreSQL is running
- Redis is running
- migrations have been applied

Start Django:

```bash
python manage.py runserver
```

Expected output includes:

```text
Starting development server at http://127.0.0.1:8000/
```

Open:

```text
http://127.0.0.1:8000/
```

Django Admin:

```text
http://127.0.0.1:8000/admin/
```

Stop the development server with:

```text
CTRL + C
```

or the appropriate terminal interrupt command.

---

## 13. Start the RQ Worker

Video processing jobs are queued through Django RQ.

The worker must run separately from the Django development server.

Open a **second terminal**.

Enter the backend directory:

```bash
cd videoflix/backend
```

Activate the virtual environment.

### Windows

```powershell
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

Start the default queue worker:

```bash
python manage.py rqworker default
```

The worker listens for video processing jobs.

### Recommended Development Terminals

A normal development setup therefore uses:

```text
Terminal 1
──────────
python manage.py runserver


Terminal 2
──────────
python manage.py rqworker default


Docker Desktop
──────────────
PostgreSQL
Redis
```

### Windows RQ Limitation

The project can enqueue RQ jobs on Windows, but some RQ worker implementations rely on Unix-specific process functionality.

A Windows worker may produce errors such as:

```text
AttributeError: module 'os' has no attribute 'wait4'
```

This is an RQ/Windows process compatibility issue.

For reliable background processing, especially in production, run the RQ worker in a Linux environment.

---

# Environment Variables

The Django settings load `.env` using `python-dotenv`.

The following environment variables are required:

| Variable | Purpose | Local Example |
|---|---|---|
| `SECRET_KEY` | Django secret key | `your-secret-key` |
| `DEBUG` | Django debug mode | `True` |
| `POSTGRES_DB` | PostgreSQL database | `videoflix` |
| `POSTGRES_USER` | PostgreSQL user | `videoflix` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `your-secure-password` |
| `POSTGRES_HOST` | PostgreSQL hostname | `localhost` |
| `POSTGRES_PORT` | PostgreSQL port | `5432` |
| `REDIS_URL` | Redis connection | `redis://localhost:6379/1` |

The `.env.example` should therefore contain:

```env
POSTGRES_DB=videoflix
POSTGRES_USER=videoflix
POSTGRES_PASSWORD=

POSTGRES_HOST=localhost
POSTGRES_PORT=5432

REDIS_URL=redis://localhost:6379/1

SECRET_KEY=
DEBUG=True
```

The empty values are intentional placeholders.

A developer cloning the repository creates `.env` from this template and fills in the required secrets.

---

# Docker Services

The Docker Compose configuration provides PostgreSQL and Redis.

## PostgreSQL Service

Image:

```text
postgres:17
```

Container:

```text
videoflix_db
```

Port:

```text
5432:5432
```

Persistent volume:

```text
postgres_data
```

## Redis Service

Image:

```text
redis:7-alpine
```

Container:

```text
videoflix_redis
```

Port:

```text
6379:6379
```

Persistent volume:

```text
redis_data
```

## Show Running Containers

```bash
docker ps
```

## Show Compose Services

```bash
docker compose ps
```

## View PostgreSQL Logs

```bash
docker logs videoflix_db
```

## View Redis Logs

```bash
docker logs videoflix_redis
```

---

# Database

Videoflix uses PostgreSQL.

Django reads the database configuration from `.env`.

The configuration corresponds to:

```text
Database: PostgreSQL
Host: localhost
Port: 5432
Database name: POSTGRES_DB
Username: POSTGRES_USER
Password: POSTGRES_PASSWORD
```

Apply migrations after starting PostgreSQL:

```bash
python manage.py migrate
```

Check migration status:

```bash
python manage.py showmigrations
```

---

# Redis and Django RQ

Redis is used by:

- Django cache configuration
- Django RQ
- Background video processing jobs

The local Redis URL is:

```env
REDIS_URL=redis://localhost:6379/1
```

Django RQ uses the `default` queue.

The configured default job timeout is:

```text
900 seconds
```

The processing task is located in:

```text
videos/tasks.py
```

The FFmpeg processing logic is located in:

```text
videos/functions.py
```

---

# FFmpeg and Video Processing

FFmpeg processes uploaded videos and generates HLS output.

Supported output resolutions are:

- 480p
- 720p
- 1080p

The generated directory structure follows the movie ID.

Example for movie ID `3`:

```text
hls/
└── 3/
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

Depending on video duration, HLS output may contain multiple `.ts` segment files.

The `.m3u8` file is the HLS playlist.

The `.ts` files contain the actual video segments.

---

# Django Admin

Video uploads are handled through Django Admin.

Start Django:

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/admin/
```

Log in using the superuser created during installation.

From the Video administration section, create/upload a video.

After the video is saved:

```text
Video saved
     ↓
post_save
     ↓
Job added to RQ queue
     ↓
RQ worker receives job
     ↓
process_video()
     ↓
FFmpeg generates HLS
```

---

# Authentication

Videoflix uses JWT authentication.

The configured authentication class is:

```text
accounts.api.authentication.CookieJWTAuthentication
```

The project uses:

- Access token
- Refresh token
- Token blacklist

## Token Lifetimes

Access token:

```text
30 minutes
```

Refresh token:

```text
7 days
```

## Bearer Authentication

When testing an authenticated endpoint with a bearer token:

```http
Authorization: Bearer <ACCESS_TOKEN>
```

Use the **access token**, not the refresh token.

Example:

```text
Authorization
Type: Bearer Token
Token: <ACCESS_TOKEN>
```

If an access token has expired, log in again or use the configured refresh flow to obtain a new access token.

---

# API Endpoints

## Register

```http
POST /api/register/
```

Creates a new user account.

---

## Login

```http
POST /api/login/
```

Authenticates a user.

The login endpoint provides the authentication information required for subsequent protected requests.

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

Used to obtain a new access token through the refresh flow.

---

## Get Videos

```http
GET /api/video/
```

Returns the available videos.

### Authentication

JWT authentication is required.

### Success

```text
200 OK
```

### Example

```text
http://127.0.0.1:8000/api/video/
```

---

## Get HLS Manifest

```http
GET /api/video/<int:movie_id>/<str:resolution>/index.m3u8
```

Returns the HLS playlist for a specific movie and resolution.

### URL Parameters

| Parameter | Description |
|---|---|
| `movie_id` | ID of the movie |
| `resolution` | Requested resolution such as `480p`, `720p` or `1080p` |

### Example

```http
GET /api/video/3/480p/index.m3u8
```

### Authentication

JWT authentication is required.

### Success Response

```text
200 OK
```

Content type:

```text
application/vnd.apple.mpegurl
```

The response body contains the HLS manifest in M3U8 format.

### Error Response

```text
404 Not Found
```

Returned if the requested video or manifest does not exist.

---

## Get HLS Segment

```http
GET /api/video/<int:movie_id>/<str:resolution>/<str:segment>/
```

Returns an individual HLS video segment for the requested movie and resolution.

### URL Parameters

| Parameter | Description |
|---|---|
| `movie_id` | ID of the movie |
| `resolution` | Requested resolution |
| `segment` | Segment filename |

### Example

```http
GET /api/video/3/480p/index0.ts
```

### Authentication

JWT authentication is required.

### Success Response

```text
200 OK
```

Content type:

```text
video/MP2T
```

The response body contains binary MPEG transport stream video data.

Because this is binary data, Postman may not display readable content in the response body.

A `200 OK` response together with `Content-Type: video/MP2T` confirms that the segment was returned successfully.

### Error Response

```text
404 Not Found
```

Returned if the requested video or segment does not exist.

---

# HLS Streaming

HLS streaming works by first requesting a playlist.

Example:

```http
GET /api/video/3/480p/index.m3u8
```

The playlist contains references to one or more video segments.

For example:

```text
index0.ts
```

The client then requests the segment:

```http
GET /api/video/3/480p/index0.ts
```

For longer videos, the player requests additional segments as playback continues.

This means the client does not need to download the entire source video before playback can begin.

---

# Testing with Postman

A recommended API testing sequence is:

```text
1. Register user
       ↓
2. Login
       ↓
3. Obtain/use access token
       ↓
4. Request video list
       ↓
5. Request HLS manifest
       ↓
6. Request HLS segment
       ↓
7. Test 404 responses
```

## Authentication in Postman

Open the request.

Select:

```text
Authorization
```

Choose:

```text
Bearer Token
```

Insert the current access token.

Do not manually insert only:

```text
eyJ...
```

into an `Authorization` header without the `Bearer` prefix.

If using the Headers tab manually, the format must be:

```text
Authorization: Bearer <ACCESS_TOKEN>
```

---

# Testing the HLS Endpoints

Assume:

```text
movie_id = 3
resolution = 480p
```

## Manifest Success Test

Request:

```http
GET http://127.0.0.1:8000/api/video/3/480p/index.m3u8
```

Expected:

```text
200 OK
```

Content type:

```text
application/vnd.apple.mpegurl
```

## Manifest 404 Test

Use a movie ID or manifest that does not exist.

Expected:

```text
404 Not Found
```

## Segment Success Test

Request:

```http
GET http://127.0.0.1:8000/api/video/3/480p/index0.ts
```

Expected:

```text
200 OK
```

Content type:

```text
video/MP2T
```

Postman may display an empty/unreadable body because the response contains binary video data.

## Segment 404 Test

Request a segment that does not exist:

```http
GET http://127.0.0.1:8000/api/video/3/480p/fake.ts
```

Expected:

```text
404 Not Found
```

---

# Django Checks and Tests

## System Check

Run:

```bash
python manage.py check
```

Expected:

```text
System check identified no issues (0 silenced).
```

## Migrations

Check migrations:

```bash
python manage.py showmigrations
```

Apply migrations:

```bash
python manage.py migrate
```

## Django Tests

Run:

```bash
python manage.py test
```

---

# Generated Files

Video processing creates local/generated files.

These should not be committed to Git.

The `.gitignore` should exclude:

```gitignore
# Environment
.env
.env.*

# Python
**pycache**/
*.py[cod]
*$py.class

# Virtual environment
venv/
.venv/
env/

# Django
*.log
db.sqlite3
media/
staticfiles/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Local video processing output
hls/
thumbnails/
videos/*.mp4
```

## Important `.env.example` Note

If `.gitignore` contains:

```gitignore
.env.*
```

then `.env.example` also matches this pattern.

If `.env.example` should be tracked by Git, add this exception after the `.env.*` rule:

```gitignore
!.env.example
```

The environment section should therefore preferably be:

```gitignore
# Environment
.env
.env.*
!.env.example
```

Then check:

```bash
git status
```

The `.env.example` file should be trackable, while `.env` remains ignored.

---

# Troubleshooting

## `ModuleNotFoundError: No module named 'django_rq'`

This commonly happens when Django is started without the project's virtual environment.

Activate it first.

### Windows

```powershell
venv\Scripts\activate
```

Then:

```bash
pip install -r requirements.txt
```

Verify:

```bash
pip show django-rq
```

Then:

```bash
python manage.py check
```

---

## PostgreSQL Connection Refused

Example error:

```text
connection to server at "localhost", port 5432 failed
```

First make sure Docker Desktop is running.

Check:

```bash
docker ps
```

If the containers are not running:

```bash
docker compose up -d
```

Check again:

```bash
docker compose ps
```

Then:

```bash
python manage.py migrate
```

---

## Redis Connection Refused

Check the Redis container:

```bash
docker ps
```

The container should include:

```text
videoflix_redis
```

If it is missing:

```bash
docker compose up -d
```

Verify the `.env` value:

```env
REDIS_URL=redis://localhost:6379/1
```

---

## Django Cannot Resolve Host `db`

If Django runs locally and you receive a hostname error for:

```text
db
```

check `.env`.

For the local setup documented here, use:

```env
POSTGRES_HOST=localhost
```

The hostname:

```text
db
```

is the Docker Compose service name and is intended for applications running inside the Docker network.

---

## Django Cannot Resolve Host `redis`

For local Django, use:

```env
REDIS_URL=redis://localhost:6379/1
```

not:

```env
REDIS_URL=redis://redis:6379/1
```

The hostname `redis` is available inside the Docker Compose network.

---

## FFmpeg Not Found

Run:

```bash
ffmpeg -version
```

If the command is not found, install FFmpeg and make sure its executable directory is available through the operating system PATH.

After changing PATH on Windows, restart PowerShell or VS Code.

---

## RQ Worker Error on Windows

A Windows RQ worker may produce:

```text
AttributeError: module 'os' has no attribute 'wait4'
```

This is related to RQ worker process handling on Windows.

The Django application and Redis queue configuration can still work, but reliable RQ background workers should be run in a Linux-compatible environment.

---

## `401 Unauthorized`

Make sure a valid access token is being used.

In Postman:

```text
Authorization
→ Bearer Token
→ <ACCESS_TOKEN>
```

Access tokens expire after 30 minutes according to the current project settings.

If the token has expired, obtain a new access token.

---

## HLS Manifest Returns 404

Check that:

1. The video exists.
2. The video has been processed.
3. The requested resolution exists.
4. The generated `index.m3u8` exists.

Example:

```text
hls/3/480p/index.m3u8
```

---

## HLS Segment Returns 404

Check the generated HLS directory.

Example:

```text
hls/3/480p/
```

Verify the actual segment filename.

For example:

```text
index0.ts
```

Then request exactly that filename.

---

## Postman Shows Nothing for the `.ts` Response

This is expected.

The HLS segment endpoint returns binary video data:

```text
Content-Type: video/MP2T
```

Postman does not display binary MPEG transport stream data as readable JSON or text.

Check:

```text
200 OK
```

and the response content type/size instead.

---

# Clean Setup from Scratch

This is the complete quick-start sequence for a new developer.

## Windows PowerShell

```powershell
git clone <YOUR_REPOSITORY_URL>

cd videoflix
cd backend

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

Copy-Item .env.example .env
```

Now edit `.env` and configure:

```env
POSTGRES_DB=videoflix
POSTGRES_USER=videoflix
POSTGRES_PASSWORD=your-secure-password

POSTGRES_HOST=localhost
POSTGRES_PORT=5432

REDIS_URL=redis://localhost:6379/1

SECRET_KEY=your-django-secret-key
DEBUG=True
```

Then:

```powershell
docker compose up -d

docker ps

python manage.py migrate

python manage.py createsuperuser

python manage.py check

ffmpeg -version

python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/admin/
```

For background processing, open another terminal:

```powershell
cd videoflix\backend

venv\Scripts\activate

python manage.py rqworker default
```

> On Windows, see the RQ worker limitation described in the troubleshooting section.

---

# Development Workflow

A clean development workflow is:

```text
Create / activate virtual environment
              ↓
Start Docker services
              ↓
PostgreSQL + Redis running
              ↓
Start Django
              ↓
Start RQ worker where supported
              ↓
Implement feature
              ↓
python manage.py check
              ↓
Test API with Postman
              ↓
Test success case
              ↓
Test error case
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

```bash
docker compose up -d
```

```bash
python manage.py check
```

```bash
python manage.py runserver
```

```bash
python manage.py test
```

```bash
git status
```

---

# Author

**Moha Broha**

Fullstack Developer in Training