# Payment (ระบบทำจ่ายอัตโนมัติ) — Setup Manual

คู่มือขั้นตอนการตั้งค่าระบบ `payment` (แอป Django ใหม่ใน `backend/payment/` + หน้าเว็บใน `frontend/src/app/payment/`) ตั้งแต่เริ่มต้นจนพร้อมใช้งานจริง เอกสารนี้ครอบคลุมเฉพาะ **การตั้งค่า/onboarding** ไม่ใช่ business logic แบบละเอียด (ดู business rule จริงได้จากโค้ด `backend/payment/services.py`)

ระบบนี้ **ไม่มี approval engine ของตัวเอง** — ผูกกับ `workflow` app เดิมทั้งหมดผ่าน `PaymentVoucher.request` (OneToOne ไปยัง `workflow.Request`) ดังนั้นก่อนใช้งาน payment ได้ ต้องมีโครงอนุมัติของ `workflow` พร้อมก่อนเสมอ

---

## ภาพรวมลำดับการตั้งค่า

```
1. สร้าง Django Groups สำหรับผู้อนุมัติ
2. ตรวจ/ตั้งค่า Department + manager (ถ้าจะใช้ step แบบหัวหน้าแผนก)
3. สร้าง WorkflowConfig + WorkflowStep สำหรับ payment (1 ชุดขึ้นไป)
4. สร้าง PaymentApprovalTier ผูกวงเงิน → WorkflowConfig
5. ตั้งค่า PVNumberingConfig (ไม่บังคับ มี default ให้)
6. Import ข้อมูล Supplier + บัญชีธนาคาร
7. (ถ้าต้องการ) Backfill ทะเบียนสินทรัพย์เดิมจาก excel
8. ตรวจสอบความพร้อม (checklist ท้ายเอกสาร) แล้วเริ่มใช้งานจริง
```

---

## ขั้นตอนที่ 1 — สร้าง Django Groups สำหรับผู้อนุมัติ

เข้า `/admin/auth/group/` (Django admin) แล้วสร้างกลุ่มตามระดับการอนุมัติที่ต้องการ ตัวอย่าง:

- `Payment Approver - VP`
- `Payment Approver - CEO`

จากนั้นเพิ่มผู้ใช้จริงเข้ากลุ่มที่ `/admin/auth/user/` → เลือก user → ส่วน "Groups"

> ตั้งชื่อกลุ่มอย่างไรก็ได้ ไม่ผูกกับโค้ด — แค่ต้องเลือกกลุ่มที่ถูกต้องตอนสร้าง `WorkflowStep` ในขั้นตอนที่ 3

---

## ขั้นตอนที่ 2 — ตรวจสอบ Department / หัวหน้าแผนก (ถ้าต้องการ step แบบนี้)

ที่ `/admin/users/department/` ตรวจสอบว่าแต่ละแผนกมี field `manager` (หัวหน้าแผนก) ถูกต้อง เพราะ step ที่ตั้ง `is_department_manager=True` จะ resolve ผู้อนุมัติจาก `creator.profile.department.manager` โดยอัตโนมัติ — ถ้าไม่ตั้ง manager ไว้ ระบบจะหาไม่เจอและ log warning (คำขอจะค้างไม่มีคนอนุมัติ step นั้น)

---

## ขั้นตอนที่ 3 — สร้าง WorkflowConfig + WorkflowStep สำหรับ payment

ที่ `/admin/workflow/workflowconfig/` สร้าง config อย่างน้อย 1 ชุด (แนะนำสร้างแยกตามระดับวงเงินถ้าจะใช้ approval ตามมูลค่า):

**ตัวอย่าง Config A — "Payment วงเงินเล็ก"**
| step_number | step_name | is_department_manager | required_group |
|---|---|---|---|
| 1 | หัวหน้าแผนกอนุมัติ | ✅ | — |
| 2 | VP อนุมัติ | ❌ | `Payment Approver - VP` |

**ตัวอย่าง Config B — "Payment วงเงินใหญ่"**
| step_number | step_name | is_department_manager | required_group |
|---|---|---|---|
| 1 | หัวหน้าแผนกอนุมัติ | ✅ | — |
| 2 | CEO อนุมัติ | ❌ | `Payment Approver - CEO` |

> ถ้าต้องการ**อนุมัติแบบตายตัว** (ไม่สนวงเงิน) สร้าง config เดียวพอ แล้วในขั้นตอนที่ 4 สร้าง tier เดียวครอบคลุมทุกวงเงิน

---

## ขั้นตอนที่ 4 — สร้าง PaymentApprovalTier

เรียก API หรือใช้ Django admin (`/admin/payment/paymentapprovaltier/`):

```
POST /api/v1/payment/approval-tiers/
{
  "name": "วงเงินเล็ก",
  "min_amount": 0,
  "max_amount": 2500,
  "workflow_config": <id ของ Config A>,
  "is_active": true,
  "order": 1
}
```
```
POST /api/v1/payment/approval-tiers/
{
  "name": "วงเงินใหญ่",
  "min_amount": 2500,
  "max_amount": 250000,
  "workflow_config": <id ของ Config B>,
  "is_active": true,
  "order": 2
}
```

**สำคัญ**: ต้องมี tier ครอบคลุมทุกช่วงยอดเงินที่เป็นไปได้ ไม่งั้นตอนสร้าง voucher ที่ยอดหลุดช่วงจะได้ error (`PaymentApprovalTier.resolve_for_amount` ตั้งใจไม่ fallback เงียบๆ) — ถ้าไม่แน่ใจ ให้ตั้งแถวสุดท้ายเป็น `max_amount: null` (ไม่จำกัด) เพื่อกันยอดที่สูงเกินคาด

---

## ขั้นตอนที่ 5 — PVNumberingConfig (ไม่บังคับ)

ถ้าไม่ตั้งค่าอะไร ระบบจะสร้าง config default ให้อัตโนมัติ (`prefix="PV"`, pattern `PV{seq:02d}/{running:03d}`, reset รายปี) ถ้าต้องการรูปแบบอื่นให้ตรงกับที่ฝ่ายบัญชีใช้อยู่เดิม แก้ที่ `/admin/payment/pvnumberingconfig/`:
- `prefix`, `pattern` (placeholder: `{prefix}`, `{seq}`, `{running}`)
- `reset_period`: `NEVER` / `YEARLY` / `MONTHLY`

---

## ขั้นตอนที่ 6 — Import ข้อมูล Supplier

เตรียมไฟล์ CSV/XLSX ที่มีคอลัมน์ (ชื่อคอลัมน์ต้องตรงเป๊ะ):

```
name, tax_id, branch_type, address, phone, email, bank_name, branch, account_no, account_name
```

รันคำสั่ง (ใน container backend):
```bash
docker compose exec backend python manage.py import_suppliers --file /path/to/suppliers.csv
```

คำสั่งนี้ **idempotent by `tax_id`** — รันซ้ำได้โดยไม่สร้างข้อมูลซ้ำ (จะ update แทน) เลขบัญชีธนาคารในไฟล์จะถูกสร้างเป็นบัญชี `is_current=True` ของแต่ละ supplier — **ตรวจสอบความถูกต้องของเลขบัญชีในไฟล์ก่อน import เสมอ** เพราะระบบจะเชื่อว่านี่คือบัญชีที่ verify แล้ว

---

## ขั้นตอนที่ 7 — Backfill ทะเบียนสินทรัพย์เดิม (ถ้ามีไฟล์ ค่าเสื่อมราคา เก่า)

```bash
docker compose exec backend python manage.py import_depreciation_excel --file /path/to/ค่าเสื่อมราคา_MM-YYYY.xlsx
```

คำสั่งนี้อ่านไฟล์ตามโครงสร้างจริงที่พบ (1 sheet ต่อปี, มีแถวหัวข้อหมวดหมู่คั่นในชีตเดียว ไม่ใช่แยกชีตต่อหมวด) แล้ว map เข้า `FixedAsset` + `DepreciationEntry` โดย:
- อ่านคอลัมน์ ทรัพย์สิน/PV number/วันที่/ราคา/อัตรา/JAN-DEC ตามตำแหน่งที่ fix ไว้ในโค้ด (ดู comment ใน `import_depreciation_excel.py` ถ้าโครงสร้างไฟล์เปลี่ยนต้องแก้โค้ดตาม)
- เก็บเลข PV เดิมไว้ที่ `legacy_pv_ref` (ไม่ใช่ FK จริงเพราะ voucher เก่าไม่ได้อยู่ในระบบใหม่)
- ไฟล์นี้อาจมีบาง sheet ขนาดใหญ่ผิดปกติ — คำสั่ง stream อ่านแบบ read-only อยู่แล้ว ไม่ต้องกังวลเรื่อง memory

---

## Checklist ก่อนประกาศว่า "พร้อมใช้งาน"

- [ ] มี Group ผู้อนุมัติอย่างน้อย 1 กลุ่ม และมีผู้ใช้จริงอยู่ในกลุ่มแล้ว
- [ ] Department ที่เกี่ยวข้องมี `manager` ตั้งไว้ครบ (ถ้าใช้ step หัวหน้าแผนก)
- [ ] มี `WorkflowConfig` + `WorkflowStep` สำหรับ payment อย่างน้อย 1 ชุด และทดสอบ sequence step ถูกต้อง
- [ ] มี `PaymentApprovalTier` ครอบคลุมทุกช่วงวงเงิน (มีแถว `max_amount: null` ปิดท้ายเสมอ)
- [ ] Import supplier แล้วสุ่มตรวจเลขบัญชีธนาคารถูกต้องจริง 2-3 ราย
- [ ] (ถ้าต้อง) backfill ทะเบียนสินทรัพย์แล้วสุ่มตรวจยอดค่าเสื่อมราคาตรงกับ excel เดิม
- [ ] ทดสอบ end-to-end 1 รอบจริง: อัปโหลดเอกสารทดสอบ → AI extract → สร้าง voucher → อนุมัติผ่านทุก step → mark-paid สำเร็จ
- [ ] Celery worker รันอยู่จริง (AI extraction เป็น async task ผ่าน Celery — ถ้า worker ไม่รัน เอกสารจะค้างสถานะ `PENDING` ตลอด)

เมื่อผ่านครบทุกข้อ ระบบพร้อมให้ user จริงเริ่มอัปโหลดเอกสารและสร้าง payment voucher ได้
