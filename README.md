# 🚀 xInvest: Intelligent Investment & Fund Analysis Platform

[![Django](https://img.shields.io/badge/Backend-Django%205.2-092E20?style=for-the-badge&logo=django)](https://www.djangoproject.com/)
[![Next.js](https://img.shields.io/badge/Frontend-Next.js%2016-000000?style=for-the-badge&logo=next.js)](https://nextjs.org/)
[![Go](https://img.shields.io/badge/Service-Go%20Trading-00ADD8?style=for-the-badge&logo=go)](https://go.dev/)
[![Flutter](https://img.shields.io/badge/Mobile-Flutter-02569B?style=for-the-badge&logo=flutter)](https://flutter.dev/)
[![LangChain](https://img.shields.io/badge/AI-LangChain%20%2B%20Gemini-121212?style=for-the-badge&logo=chainlink)](https://langchain.com/)

**xInvest** is a comprehensive, multi-platform investment ecosystem designed for modern investors. It leverages AI-driven sentiment analysis, advanced portfolio optimization, and a high-performance trading engine to provide actionable financial insights.

---

## 🌟 Key Features

### 🧠 AI-Powered Insights
- **Automated News Analysis**: Integrated with **Google Gemini** and **LangChain** to extract sentiment and key insights from financial news in real-time.
- **Sentiment Scoring**: Dynamic scoring for funds based on historical and current market data.

### 📈 Portfolio & Fund Management
- **Optimization**: Uses `PyPortfolioOpt` and `yfinance` for modern portfolio theory applications and risk management.
- **FundConnext Integration**: Seamless data ingestion and management for financial funds (stt_fundconnext).
- **Interactive Dashboards**: Rich data visualizations using `Recharts`, `Tremor`, and `fl_chart`.

### ⚡ High-Performance Trading
- **Go-Trading Engine**: A dedicated high-concurrency service written in **Go (Gin)** for managing trading signals and execution.
- **Real-time Pipeline**: Asynchronous task processing using **Celery** and **Redis**.

---

## 🛠️ Technology Stack

### Backend (The Core)
- **Framework**: Django 5.2 (Python)
- **API**: Django Rest Framework (DRF), GraphQL (Graphene), PostgREST
- **Async Processing**: Celery, Redis
- **Database**: PostgreSQL
- **AI/ML**: Google Generative AI, LangChain, Pandas, NumPy, PyPortfolioOpt

### Frontend & Mobile
- **Web**: Next.js 16+, TypeScript, Tailwind CSS v4, Shadcn UI
- **Mobile**: Flutter (iOS/Android)
- **Charts**: Recharts, Tremor (@tremor/react), fl_chart

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Reverse Proxy**: Nginx
- **Monitoring**: Celery Flower

---

## 🏗️ Architecture Overview

xInvest is structured as a modular monolith with decoupled high-performance services:

1.  **Django Backend**: Handles user management, fund logic, AI orchestration, and complex financial calculations.
2.  **Go Trading Service**: Manages high-frequency trading data and execution logic.
3.  **Next.js Frontend**: A premium, responsive web interface for investors and operators.
4.  **Flutter Mobile**: Cross-platform mobile access for on-the-go portfolio tracking.
5.  **PostgREST & GraphQL**: Provide flexible and efficient data access layers.

---

## 🚀 Getting Started

### Prerequisites
- Docker & Docker Compose
- Flutter SDK (for mobile development)
- Node.js & npm (for frontend development)

### Quick Start with Docker
```bash
# Clone the repository
git clone https://github.com/yourusername/xInvest.git
cd xInvest

# Start the development stack
docker compose -f docker-compose.dev.yml up -d --build

# Run migrations
docker compose exec backend python manage.py migrate
```

- **Investor Portal**: [http://localhost:3000](http://localhost:3000)
- **Admin Portal**: [http://localhost:3000/admin-portal](http://localhost:3000/admin-portal)
- **API Documentation**: [http://localhost:8000/api/schema/swagger-ui/](http://localhost:8000/api/schema/swagger-ui/)

---

## 📸 Screenshots
*(Add your stunning UI screenshots here!)*

---

## 👨‍💻 Author
**Your Name**
- **Website**: [yourportfolio.com](https://yourportfolio.com)
- **LinkedIn**: [linkedin.com/in/yourprofile](https://linkedin.com/in/yourprofile)
- **GitHub**: [@yourusername](https://github.com/yourusername)

---
*Created as part of the xInvest project portfolio.*
