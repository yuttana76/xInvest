# Django Register API Implementation Plan

แผนการพัฒนาระบบสมัครสมาชิก (Register REST API) สำหรับระบบ backend ด้วย Django และ Django REST Framework (DRF) ที่รองรับการยืนยันอีเมลด้วย OTP, วันที่สมัคร, เบอร์โทรศัพท์มือถือ และระบบตรวจสอบความปลอดภัย (Validation)

---

## 1. ข้อแนะนำในการตรวจสอบข้อมูลสมัครสมาชิก (Validation Recommendations)

เพื่อให้ระบบมีความปลอดภัยและมีข้อมูลที่ถูกต้อง (Data Integrity) ควรมีการตรวจสอบข้อมูลในฝั่ง Backend ดังนี้:

### 1.1 การตรวจสอบการซ้ำซ้อน (Duplicate Checks)
*   **Duplicate Username:** ตรวจสอบว่ามี `username` นี้อยู่ในระบบแล้วหรือไม่ (ป้องกันการใช้ชื่อซ้ำ)
*   **Duplicate Email:** ตรวจสอบว่ามี `email` นี้ผูกกับบัญชีอื่นแล้วหรือไม่ (ป้องกันการใช้อีเมลสมัครหลายบัญชี)
*   **Duplicate Mobile Number:** ตรวจสอบว่าเบอร์โทรศัพท์ซ้ำหรือไม่ในระดับ `Profile`

### 1.2 การตรวจสอบความปลอดภัยของรหัสผ่าน (Password Strength & Security)
*   **Password Matching:** ตรวจสอบว่า `password` และ `password_confirm` มีค่าตรงกัน
*   **Password Complexity:** บังคับความยากของรหัสผ่าน เช่น:
    *   ความยาวขั้นต่ำ 8 ตัวอักษร
    *   ต้องประกอบด้วย ตัวอักษรภาษาอังกฤษตัวพิมพ์ใหญ่ (A-Z) ตัวพิมพ์เล็ก (a-z) ตัวเลข (0-9) และอักขระพิเศษอย่างน้อย 1 ตัว
*   **Prevent Common Passwords:** หลีกเลี่ยงรหัสผ่านที่ง่ายเกินไป (เช่น 12345678, password)

### 1.3 การตรวจสอบรูปแบบข้อมูล (Format Validation)
*   **Email Format:** ตรวจสอบรูปแบบอีเมลให้ถูกต้องตามมาตรฐาน RFC 5322
*   **Mobile Number Format:** ตรวจสอบว่าเบอร์โทรศัพท์เป็นตัวเลขเท่านั้น และมีความยาวที่ถูกต้อง (เช่น 9-10 หลักสำหรับเบอร์ไทย)

### 1.4 การจัดการบัญชีค้างที่ยังไม่กดยืนยัน OTP (Stale Unverified Accounts)
*   เมื่อสมัครแล้ว บัญชีจะยังไม่ถูกเปิดใช้งาน (`is_active=False`)
*   หากผู้ใช้ไม่กดยืนยัน OTP ภายในช่วงเวลาที่กำหนด (**ภายใน 1 ชั่วโมง**):
    *   **resend-otp:** ต้องมี API สำหรับขอรหัส OTP ใหม่อีกครั้ง เพื่อไม่ให้ผู้ใช้งานสมัครใหม่ไม่ได้
    *   (Option) หากผู้ใช้จะสมัครใหม่ด้วยอีเมลเดิมแต่บัญชียังทำงานค้างอยู่ในสถานะไม่เสร็จสิ้นระบบควรรองรับการทำความสะอาด (Clean up) หรืออนุญาตให้สมัครทับ/ส่ง OTP ซ้ำได้

---

## 2. การเปลี่ยนแปลงของฐานข้อมูล (Model Changes)

### 2.1 [MODIFY] [models.py](file:///Users/mpamdev03/projects/python/xInvest/backend/users/models.py)
แก้ไขโมเดล `Profile` เพื่อเพิ่มฟิลด์:
*   `mobile_number = models.CharField(max_length=15, unique=True, blank=True, null=True)` *(กำหนดเป็น unique เพื่อป้องกันเบอร์ซ้ำ)*
*   `is_email_verified = models.BooleanField(default=False)`

แก้ไขระยะเวลาของ OTP:
*   กำหนดอายุของ OTP ให้หมดอายุใน **1 ชั่วโมง** (60 นาที)

---

## 3. โครงสร้าง REST API (Endpoints)

### 3.1 Endpoint 1: Register (สมัครสมาชิก & ส่ง OTP)
*   **Path:** `/api/v1/auth/register/`
*   **Method:** `POST`
*   **Request Body (JSON):**
    ```json
    {
      "username": "user123",
      "email": "user123@example.com",
      "password": "Password123!",
      "password_confirm": "Password123!",
      "first_name": "John",
      "last_name": "Doe",
      "mobile_number": "0812345678"
    }
    ```
*   **Logic การตรวจสอบ (Serializer Validation):**
    1. ตรวจสอบว่า `password` และ `password_confirm` ตรงกัน
    2. ตรวจสอบความปลอดภัยของ `password` (ตัวพิมพ์ใหญ่, เล็ก, ตัวเลข, อักขระพิเศษ, ความยาว >= 8)
    3. ตรวจสอบรูปแบบ `email` และความซ้ำในตาราง `User`
    4. ตรวจสอบรูปแบบ `mobile_number` และความซ้ำในตาราง `Profile`
*   **Response (201 Created):**
    ```json
    {
      "message": "Registration successful. Please verify your email with the OTP sent.",
      "username": "user123",
      "email": "user123@example.com",
      "otp_ref": "a7b3c9",
      "register_date": "2026-05-27T17:00:43Z"
    }
    ```

### 3.2 Endpoint 2: Verify Registration OTP (ยืนยัน OTP)
*   **Path:** `/api/v1/auth/register/verify/`
*   **Method:** `POST`
*   **Request Body:**
    ```json
    {
      "username": "user123",
      "otp_code": "123456"
    }
    ```
*   **Response (200 OK):**
    ```json
    {
      "message": "Email verified successfully. Your account is now active.",
      "username": "user123",
      "is_active": true
    }
    ```

### 3.3 Endpoint 3: Resend Registration OTP
*   **Path:** `/api/v1/auth/register/resend-otp/`
*   **Method:** `POST`
*   **Request Body:**
    ```json
    {
      "username": "user123"
    }
    ```
*   **Logic:** สร้าง OTP ชุดใหม่และส่งอีเมลอีกครั้งให้กับผู้ใช้งานที่ยังยืนยันตัวตนไม่สำเร็จ (`is_active = False`)

---

## 4. ขั้นตอนการดำเนินการ (Action Plan)

1.  **ปรับปรุงโมเดล:** อัปเดตโมเดล `Profile` ใน [models.py](file:///Users/mpamdev03/projects/python/xInvest/backend/users/models.py)
2.  **รันคำสั่ง DB Migration:** สร้างไฟล์ migration และรันเพื่อปรับปรุง Database schema
3.  **เขียน Serializers & Validators:** ใน [serializers.py](file:///Users/mpamdev03/projects/python/xInvest/backend/users/serializers.py)
4.  **เขียน Views & Logic:** ใน [views.py](file:///Users/mpamdev03/projects/python/xInvest/backend/users/views.py)
5.  **เพิ่ม URL Routes:** ใน [urls.py](file:///Users/mpamdev03/projects/python/xInvest/backend/users/urls.py)

---

## Verification Plan
*   ทำการเขียน Unit tests หรือทดสอบด้วย HTTP Client ในการจำลองการส่งข้อมูลที่ถูกและผิดรูปแบบ เพื่อเช็คระบบ Validation ทั้งหมด