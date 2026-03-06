# Context: Investment Portfolio Management System (Django + Next.js)

ระบบดูแลลูกค้าด้านการลงทุน ที่ครอบคลุมการวิเคราะห์พอร์ต (Portfolio Analysis) และการแนะนำการลงทุน (Rebalancing/Recommendation) โดยใช้โครงสร้าง Microservices ด้วย Docker

---

## 🏗️ 1. Project Structure & Architecture

```text
invest-platform/
├── backend/             # Django REST Framework (API, Logic, Analytics)
│   ├── Dockerfile       # Python 3.11-slim
│   ├── requirements.txt # Django, DRF, Pandas, NumPy, PyPortfolioOpt, psycopg2-binary
│   └── ...
├── frontend/            # Next.js (Dashboard, Visualization)
│   ├── Dockerfile       # Node 20-alpine
│   ├── package.json     # NextAuth, TanStack Query, Tremor, Recharts, Tailwind
│   └── ...
├── nginx/               # Reverse Proxy
│   └── conf.d/default.conf
├── backups/             # Database snapshots
├── docker-compose.yml   # Multi-container orchestration
├── .env.production      # Secret keys & configurations
└── backup_db.sh         # PostgreSQL backup script
```

🛠️ 2. Core Technical SpecificationsBackend (Django)Database: PostgreSQL (Transaction-safe)Analysis Engines: Pandas สำหรับ ROI/Volatility, PyPortfolioOpt สำหรับ Sharpe Ratio และ Efficient FrontierAsync Tasks: Celery + Redis สำหรับดึงราคาหุ้นรายวัน (EOD) และคำนวณพอร์ตหลังบ้านAuth: JWT (SimpleJWT) เชื่อมต่อกับ NextAuth.jsFrontend (Next.js)Rendering: SSR สำหรับหน้า Dashboard เพื่อข้อมูลที่สดใหม่UI: Tremor.so สำหรับหน้า Dashboard การเงิน และ Tailwind CSSData Fetching: TanStack Query สำหรับจัดการ Cache และ Auto-refetch ข้อมูลราคา🔒 3. Environment Configuration (.env.production)Bash# Django
DEBUG=False
SECRET_KEY=prod_secret_key
ALLOWED_HOSTS=api.yourdomain.com
DATABASE_URL=postgres://user:pass@db:5432/db

# Next.js

NEXT_PUBLIC_API_URL=[https://api.yourdomain.com](https://api.yourdomain.com)
NEXTAUTH_SECRET=auth_secret

# External APIs

FINANCE_API_KEY=your_key_here
🚀 4. Deployment & Operation CommandsBuild & Run: docker-compose up -d --buildMigration: docker-compose exec backend python manage.py migrateSuperuser: docker-compose exec backend python manage.py createsuperuserManual Backup: ./backup_db.sh📊 5. Financial Logic ReferenceSharpe Ratio: $\frac{E(R_p) - R_f}{\sigma_p}$Rebalancing Rule: แจ้งเตือนเมื่อสัดส่วนสินทรัพย์ปัจจุบันเบี่ยงเบนจาก Model Portfolio เกิน $\pm 5\%$Data Source: ดึงข้อมูลผ่าน yfinance หรือ SET API และพักข้อมูลใน Redis (TTL 5 mins)📝 6. Next Steps for ImplementationModel Portfolio: สร้าง Table สำหรับเก็บพอร์ตตัวอย่างตามระดับความเสี่ยงRebalancing Engine: เขียน Logic ใน Django เพื่อคำนวณส่วนต่าง (Gap) ระหว่างพอร์ตจริงกับพอร์ตแนะนำSSL Setup: คอนฟิก Certbot ใน Nginx เพื่อรัน HTTPSNotification: ระบบแจ้งเตือนลูกค้าผ่าน Email/Line เมื่อถึงเวลาปรับพอร์ต

---

**คุณต้องการให้ผมช่วยเขียนโค้ดในส่วน "Rebalancing Logic" หรือ "Dashboard UI" ต่อจาก Context นี้เลยไหมครับ?**
