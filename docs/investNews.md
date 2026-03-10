## Phase 1 Implementation: Public Fund Analytics

- **Backend Goal:**
  Create new app is `investNews`
  Develop an API that aggregates fund data and news with AI-generated sentiments.

1. Backend Architecture
   หัวใจของ Backend คือการจัดการข้อมูลจากหลายแหล่งและประมวลผลด้วย AI เพื่อส่งต่อให้ผู้ใช้ทั่วไป

ก. Modules สำคัญ
Fund Aggregator Service: ใช้ Python library (yfinance, BeautifulSoup สำหรับขูดข้อมูล หรือเชื่อม API กองทุนไทย) ดึงข้อมูลราคา (NAV) และสัดส่วนการลงทุน (Holdings)

News & Sentiment Service: เชื่อมต่อ News API และใช้ Gemini API ในการวิเคราะห์เนื้อหาข่าว

Search & Recommendation: ระบบค้นหาที่รองรับ "Themes" (เช่น กองทุนยั่งยืน, กองทุน AI) โดยใช้ PostgreSQL Full-text Search

ข. Database Schema (JSONB Optimized)
Fund Table: เก็บข้อมูลพื้นฐานกองทุน (Code, Name, Risk Level, Type)
NO. Name Mandatory Max Length Format
1 Fund Code Y 30 Text
2 AMC_CODE Y 15 Text
3 Fund Name TH Y 200 Text
4 Fund Name EN Y 200 Text
5 Fund Policy Y 1 Text
6 Tax Type N 4 Text
7 FIF Flag Y 1 Text
8 Dividend_Flag Y 1 Text
9 Registration_date C 10 Date
10 Fund Risk Level Y 2 Text

FundAnalysis (JSONB Field): เก็บข้อมูลเชิงลึกที่เปลี่ยนโครงสร้างบ่อย เช่น สัดส่วนอุตสาหกรรม, ค่าธรรมเนียม, มุมมอง AI

NewsLog: เก็บข่าวสารรายวันพร้อมคะแนน Sentiment (-1 ถึง 1)

- **Frontend Goal:** Build a responsive Next.js site focused on discovery and simple investment education.
- **Key Deliverable:** A "Fund Insight" dashboard that explains market moves in plain English using Gemini AI.

2. Frontend Architecture (Next.js + Tailwind + Tremor)
   เน้นการออกแบบที่เป็น Responsive Web (เข้าผ่านมือถือได้ทันทีโดยไม่ต้องโหลดแอป) เพื่อลดแรงเสียดทาน (Friction) ของผู้ใช้ใหม่

ก. การแบ่งหน้าจอ (Screens)
Landing Page (Discovery):

แถบค้นหาขนาดใหญ่ที่รองรับคำค้นหาทั่วไป (เช่น "กองทุนลดหย่อนภาษี", "หุ้นอเมริกา")

Trending Themes: การ์ดแนะนำกลุ่มการลงทุนที่น่าสนใจในขณะนั้น

Fund Insight Page (Detail):

The Pulse Gauge: มาตรวัดความรู้สึกตลาด (Bullish/Bearish) จาก AI

Expert Insight Note: สรุปมุมมองจากผู้เชี่ยวชาญ/AI ใน 3 บรรทัด

Contextual News: รายการข่าวที่ "คัดมาแล้ว" ว่ามีผลกับกองทุนนี้จริงๆ

ข. Components ที่แนะนำ
ใช้ Tremor Library สำหรับแสดงผลกราฟและมาตรวัด (Gauges) เพราะดูเป็นมืออาชีพและโหลดเร็วมาก

3. Workflow การประมวลผล (Phase 1 Flow)
   Ingestion: Django ดึงราคาและข่าวล่าสุดทุกๆ 1 ชั่วโมง

AI Analysis: Gemini อ่านข่าวล่าสุด -> วิเคราะห์ว่ากระทบกองทุนไหน -> ให้คะแนนความน่าสนใจ

Caching: เก็บผลการวิเคราะห์ไว้ใน Redis เพื่อให้หน้าเว็บ Next.js โหลดได้เร็วระดับมิลลิวินาที

Delivery: ผู้ใช้ทั่วไปเข้ามาค้นหา -> เห็นข้อมูลวิเคราะห์ที่ "ย่อยมาให้แล้ว" -> เกิดความมั่นใจ
