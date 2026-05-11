# สร้างระบบเพื่ออ่าน fund fact sheet ส่งให้ AI วิเคราห์ตามโครงสร้าง JSON (ตัวอย่างด้านล่างนี้)

- ใน Backend fundDecision app. สร้าง model ใหม่

  class FundFactSheet(models.Model):

  # --- Identifiers ---

  fund_code = models.CharField(max_length=20, unique=True, verbose_name="รหัสกองทุน")
  fund_name_th = models.CharField(max_length=255, blank=True, verbose_name="ชื่อกองทุนภาษาไทย")
  sec_proj_id = models.CharField(max_length=50, blank=True, help_text="ID จาก SEC API")

  # --- Core Strategy & Risk ---

  risk_level = models.IntegerField(verbose_name="ระดับความเสี่ยง (1-8)")
  fund_category = models.CharField(max_length=100, help_text="เช่น Equity Large-Cap, Global Bond")
  investment_strategy = models.CharField(max_length=50, choices=[('Active', 'Active'), ('Passive', 'Passive')])

  # --- Advanced Context for AI ---

  holdings_data = models.JSONField(verbose_name="ข้อมูลการถือครองหุ้น 5-10 อันดับแรก")
  sector_allocation = models.JSONField(null=True, help_text="สัดส่วนกลุ่มอุตสาหกรรม เช่น พลังงาน 20%, แบงก์ 15%")

  # --- Currency & Global Impact ---

  is_hedged = models.BooleanField(default=False)
  hedging_policy = models.TextField(blank=True, help_text="นโยบายป้องกันความเสี่ยงค่าเงินแบบละเอียด")

  # --- Performance Metrics ---

  benchmark = models.CharField(max_length=100)
  dividend_policy = models.BooleanField(default=False, verbose_name="นโยบายจ่ายปันผล")

  # --- Metadata ---

  factsheet_data // บันทึก ไฟล์ fund fact sheet ในระบบ
  as_of_date = models.DateField(help_text="ข้อมูลใน Fact Sheet นี้เป็นข้อมูล ณ วันที่เท่าไหร่")
  updated_at = models.DateTimeField(auto_now=True)

- การบันทึก model จะทำการบันทึกใหม่เสมอไม่มีการ update key is fund_code

- Admin page FundFactSheet model ให้ทำการ upload file (pdf) หรือ มีการระบุ url link เพื่อส่งให้ AI วิเคราะห์
- บันทึกไฟล์ fund fact sheet ต้นฉบับ ที่ FundFactSheet.factsheet_data

- สร้าง Service ทำการวิเคราะห์ไฟล์ fund fact sheet ด้วย AI langGraph และ celery
  (เหมือน NewsGraphService)

System Prompt:
"คุณคือนักวิเคราะห์ข้อมูลการเงินที่มีหน้าที่สกัดข้อมูลจาก PDF Fund Fact Sheet ของกองทุนไทย กรุณาอ่านเอกสารที่แนบมาและตอบกลับเป็นรูปแบบ JSON บริสุทธิ์ (Pure JSON) เท่านั้น ห้ามมีข้อความเกริ่นนำหรือคำอธิบายเพิ่มเติม ข้อมูลต้องแม่นยำตามที่ปรากฏในเอกสาร"

User Prompt:
Plaintext
วิเคราะห์ไฟล์ PDF นี้และสกัดข้อมูลเข้าสู่โครงสร้าง JSON ดังนี้:

1. fund_code: รหัสย่อกองทุน
2. fund_name_th: ชื่อเต็มกองทุนภาษาไทย
3. risk_level: ระดับความเสี่ยง (เลข 1-8)
4. fund_category: ประเภทกลุ่มกองทุน (เช่น Equity Large-Cap)
5. investment_strategy: กลยุทธ์การลงทุน (ตอบเฉพาะ "Active" หรือ "Passive")
6. top_5_holdings: รายชื่อสินทรัพย์ 5 อันดับแรก (ระบุ name, ticker ถ้ามี, และ ratio เป็นตัวเลข %)
7. sector_allocation: สัดส่วนกลุ่มอุตสาหกรรม 5 อันดับแรก (ระบุ sector_name และ ratio %)
8. currency_hedging: นโยบายการป้องกันความเสี่ยงค่าเงิน (None/Partial/Fully/Discretionary)
9. benchmark: ดัชนีชี้วัดที่ใช้เปรียบเทียบ
10. as_of_date: วันที่ของข้อมูลพอร์ตล่าสุดในเอกสาร (รูปแบบ YYYY-MM-DD)

- ตัวอย่าง JSON Output ที่ AI จะส่งกลับมา
  {
  "fund_code": "SCBSET",
  "fund_name_th": "กองทุนเปิดไทยพาณิชย์หุ้นทุน",
  "risk_level": 6,
  "fund_category": "Equity Thai",
  "investment_strategy": "Passive",
  "top_5_holdings": [
  {"name": "DELTA", "ticker": "DELTA.BK", "ratio": 10.5},
  {"name": "PTT", "ticker": "PTT.BK", "ratio": 8.2}
  ],
  "sector_allocation": [
  {"sector_name": "ENERGY", "ratio": 22.4},
  {"sector_name": "BANKING", "ratio": 15.8}
  ],
  "currency_hedging": "None",
  "benchmark": "SET Index",
  "as_of_date": "2026-03-31"
  }
