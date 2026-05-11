# Project Context: WealthFlow (Wealth Management System)

## 🎯 Overview

ระบบบริหารจัดการความมั่งคั่ง (Portfolio Tracking, Asset Allocation, และ Investment Analysis)

- **Backend:** Django (DRF) - Focus on Data Integrity & Financial Logic.
- **Frontend:** Next.js (App Router) - Focus on Performance & Financial Visualization.

## 🛠 Tech Stack & Standards

### Backend (Django)

- **Framework:** Django 5.x + Django REST Framework (DRF).
- **Architecture:** Service Layer Pattern (แยก Business Logic ออกจาก Views).
- **Database:** PostgreSQL (Strict Schema).
- **Auth:** JWT (SimpleJWT) + Role-based Access Control (RBAC).

### Frontend (Next.js)

- **Framework:** Next.js 14+ (App Router, TypeScript).
- **State Management:** Zustand (Global) + TanStack Query (Server State).
- **UI:** Tailwind CSS + Shadcn UI + Recharts (for Financial Charts).

## 🏗 Project Structure & Best Practices

### Directory Organization

- `/backend`: Django Project Root.
  - `/core`: Settings & Main Config.
  - `/[app_name]`: Modular Apps (e.g., `investments`, `portfolios`, `users`).
  - `/services`: Business logic layer (ลดความอ้วนของ `models.py` และ `views.py`).
- `/frontend`: Next.js Project Root.
  - `/app`: Routing & Server Components.
  - `/components/features`: Complex logic components.
  - `/components/ui`: Atomic UI components (Shadcn).
  - `/hooks`: Custom Data Fetching & Logic hooks.

## 📏 Code Quality & Constraints (Strict)

- **File Size Management:** - 🛑 **MAX 500 LINES:** ห้ามแต่ละไฟล์เกิน 500 บรรทัดเด็ดขาด
  - **Modular Design:** หากไฟล์เริ่มยาว ให้แยก Logic ออกเป็น Sub-components หรือ Helper functions/Services.
- **Performance Optimization:**
  - **Django:** ใช้ `.select_related()` และ `.prefetch_related()` เสมอเพื่อเลี่ยง N+1 Problem.
  - **Next.js:** ใช้ `Image` component, Dynamic Imports สำหรับ Heavy Charts, และระบุ `prefetch={false}` ใน Link ที่ไม่จำเป็น.
- **Code Style:**
  - Backend: PEP8, Type Hinting ทุก Function.
  - Frontend: Prettier, ESLint (Strict Mode), TypeScript `strict: true`.

## 🚀 Key Workflows

1. **Investment Logic:** Calculation ทั้งหมดต้องทำที่ Backend Service Layer เท่านั้น (Frontend แสดงผลอย่างเดียว).
2. **Onboarding:** ดูคำแนะนำการติดตั้งที่ `README.md` หลักของโปรเจกต์.
