# 🔗 URL Shortener Platform

Microservices-based platform to shorten and manage URLs.  
Built using **FastAPI**, **Docker**, and planned for full scalability.

## 📦 Features

- Shorten long URLs into short, unique codes
- Redirect from short URLs to original links
- Microservices architecture (FastAPI + Docker)
- PostgreSQL-based persistence layer

## 🧱 Project Structure
```
url-shortener-platform/
├── shortener/    # Handles URL creation
├── redirector/   # Handles redirects
├── gateway/      # Entry point reverse proxy
├── infrastructure/ # Infrastructure utilitizes
├── docker-compose.yml # Service orchestration
└── README.md
```

## 🚀 Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.8 or higher (for local development)

### Installation & Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/url-shortener-platform.git
cd url-shortener-platform
```

2. Start the services using Docker Compose:
```bash
docker-compose up -d
```

The platform will be available at:
- Gateway Service: http://localhost:8080
- Shortener Service: http://localhost:8001
- Redirector Service: http://localhost:8002

### Usage

1. To shorten a URL:
```bash
curl -X POST http://localhost:8080/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/very_long_url"}'
```

2. To access a shortened URL:
```
http://localhost:8080/{short_code}
```
