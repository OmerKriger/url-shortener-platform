# 🔗 URL Shortener Platform

Microservices-based platform to shorten and manage URLs.  
Built using **FastAPI**, **Docker**, and planned for full scalability.

---

## 📦 Features

- Shorten long URLs into short, unique codes
- Redirect from short URLs to original links
- Microservices architecture (FastAPI + Docker)
- PostgreSQL-based persistence layer (coming soon)
- Reverse proxy gateway (NGINX or FastAPI-based) – planned

---

## 🧱 Project Structure
url-shortener-platform/
├── shortener/ # Handles URL creation
├── redirector/ # Handles redirects (planned)
├── gateway/ # Entry point reverse proxy (planned)
├── docker-compose.yml # Service orchestration (coming soon)
└── README.md
