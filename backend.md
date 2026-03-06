Django (Backend): หัวใจของ "สิทธิ์" (Permissions)
Django จะทำหน้าที่เป็น Single Source of Truth หรือตัวตัดสินว่าใครทำอะไรได้บ้าง โดยคุณไม่ต้องแยกโปรเจกต์ แต่ให้แยก API Endpoints และ Permissions:

Investor API (/api/v1/investor/): ใช้ IsAuthenticated permission เพื่อให้ดึงได้เฉพาะข้อมูลพอร์ตของตัวเองเท่านั้น

Admin API (/api/v1/admin/): ใช้ IsAdminUser หรือ IsStaff permission เพื่อเข้าถึงข้อมูลสรุปของลูกค้าทุกคน (Aggregation) หรือจัดการ Model Portfolio

Django Admin (Built-in): ใช้สำหรับจัดการข้อมูลดิบหลังบ้าน (เช่น แก้ไขชื่อหุ้น, ลบ User ที่มีปัญหา) โดยไม่ต้องเขียนหน้าจอเอง
