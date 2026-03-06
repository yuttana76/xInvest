# Context: Investment Portfolio Management System (Django + Next.js)

ระบบดูแลลูกค้าด้านการลงทุน ที่ครอบคลุมการวิเคราะห์พอร์ต (Portfolio Analysis) และการแนะนำการลงทุน (Rebalancing/Recommendation) โดยใช้โครงสร้าง Microservices ด้วย Docker

---

# investment-frontend

ฝั่ง Next.js (Frontend): หัวใจของ "ประสบการณ์ผู้ใช้" (UX)
Next.js จะทำหน้าที่แยก หน้าจอ (UI) ให้เหมาะสมกับบทบาทของผู้ใช้ โดยใช้ระบบ Role-Based Routing:

สำหรับ Investor (นักลงทุน)
URL: /dashboard/\*

Layout: เน้นความง่าย มีกราฟวงกลม (Pie Chart) แสดงสัดส่วนสินทรัพย์ และปุ่ม "Buy/Sell" หรือ "Rebalance"

Dashboard Components: ใช้ Tremor หรือ Recharts เพื่อแสดง Performance รายวัน

สำหรับ Admin/Advisor (ผู้ดูแล)
URL: /admin-portal/\*

Layout: มี Sidebar ที่เน้นการจัดการ เช่น "Customer List", "Market Data Management", "Risk Model Settings"

Admin Components: เน้นตาราง (Data Tables) ที่มีระบบ Filter, Search และการส่ง Notification หาพอร์ตที่ผิดปกติ
