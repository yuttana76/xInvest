# Registration API Walkthrough

ระบบสมัครสมาชิก (Register REST API) ได้รับการติดตั้งและทดสอบโครงสร้างเบื้องต้นแล้ว โดยมีการเปลี่ยนแปลงระบบ Backend ดังนี้

## การเปลี่ยนแปลงหลัก (Changes Made)

### 1. Database & Models
*   แก้ไข [models.py](file:///Users/mpamdev03/projects/python/xInvest/backend/users/models.py):
    *   เพิ่มฟิลด์ `mobile_number` (จำกัดความยาว 15 ตัวอักษร, กำหนดเป็น unique) ลงในโมเดล `Profile`
    *   เพิ่มฟิลด์ `is_email_verified` (Boolean, ค่าเริ่มต้นเป็น False) ลงในโมเดล `Profile`
    *   เปลี่ยนค่าอายุ (Expiry duration) ของรหัส OTP ในโมเดล `OTP` จากเดิม 10 นาที เป็น **60 นาที (1 ชั่วโมง)**
*   สร้างและรัน DB migrations สำเร็จ: `users.0008_profile_is_email_verified_profile_mobile_number`

### 2. Serializers & Validation
*   เพิ่ม `RegisterSerializer` ใน [serializers.py](file:///Users/mpamdev03/projects/python/xInvest/backend/users/serializers.py) พร้อมฟังก์ชันตรวจสอบ (Validation):
    *   ตรวจสอบว่า `username` และ `email` ไม่ซ้ำในตาราง `User`
    *   ตรวจสอบว่า `mobile_number` มีความยาว 9-10 หลัก และไม่ซ้ำในตาราง `Profile`
    *   ตรวจสอบรหัสผ่าน `password` และ `password_confirm` ให้มีค่าตรงกัน
    *   ตรวจสอบความซับซ้อนของรหัสผ่าน (มีความยาวอย่างน้อย 8 ตัวพิมพ์ใหญ่ ตัวพิมพ์เล็ก ตัวเลข และอักขระพิเศษ)
    *   เมื่อผ่านการตรวจสอบข้อมูล ระบบจะสร้าง `User` ใหม่โดยเซ็ตค่า `is_active = False` และสร้าง `Profile` ผูกคู่กับ `User` โดยอัปเดตค่า `mobile_number`

### 3. Views & Logic
*   เพิ่ม Views ใน [views.py](file:///Users/mpamdev03/projects/python/xInvest/backend/users/views.py):
    *   `APIRegisterView`: สำหรับสมัครสมาชิก โดยจะสร้าง User/Profile และส่งรหัส OTP 6 หลักทางอีเมล (ผ่าน Celery Queue) และส่ง OTP Reference คืนกลับไปใน response
    *   `APIRegisterVerifyView`: รับรหัส OTP เพื่อทำการตรวจสอบ หากรหัสถูกต้องและไม่หมดอายุ จะตั้งค่า `user.is_active = True` และ `profile.is_email_verified = True` **พร้อมจัดส่งอีเมลต้อนรับ "Welcome to xInvest" ผ่าน Celery Queue ทันที**
    *   `APIResendRegisterOTPView`: สำหรับขอส่งรหัส OTP เพื่อยืนยันตัวตนใหม่อีกครั้ง กรณีที่หมดอายุหรือผู้ใช้งานไม่ได้รับอีเมล

### 4. HTML Email Templates & Tasks
*   สร้าง HTML Template [welcome_email.html](file:///Users/mpamdev03/projects/python/xInvest/backend/users/templates/users/emails/welcome_email.html) ดีไซน์สีกรม-น้ำเงินหรูหราแบบเดียวกันกับระบบของ xInvest
*   เพิ่มฟังก์ชันส่งอีเมล `send_welcome_email` ใน [email_utils.py](file:///Users/mpamdev03/projects/python/xInvest/backend/users/email_utils.py)
*   เพิ่ม Celery task `task_send_welcome_email` ใน [tasks.py](file:///Users/mpamdev03/projects/python/xInvest/backend/users/tasks.py) เพื่อจัดคิวส่งอีเมลต้อนรับแบบ asynchronous เพื่อความรวดเร็วของ API

### 5. URLs
*   เพิ่ม endpoint paths ใน [urls.py](file:///Users/mpamdev03/projects/python/xInvest/backend/users/urls.py):
    *   `/api/users/register/` (APIRegisterView)
    *   `/api/users/register/verify/` (APIRegisterVerifyView)
    *   `/api/users/register/resend-otp/` (APIResendRegisterOTPView)

---

## ผลการทดสอบเชิงระบบ (Verification Results)
*   สั่งรัน `python manage.py check` ภายใน Docker Container พบว่าโครงสร้างโค้ดทั้งหมดผ่านการตรวจสอบ ไม่มีข้อผิดพลาดใดๆ:
    `System check identified no issues (0 silenced).`
