# การติดตั้ง Ollama สำหรับ Local LLM ใน xInvest

แผนการเพิ่ม Ollama เข้าสู่ระบบ Docker Compose เพื่อใช้งาน Local LLM ทดแทนหรือควบคู่กับ Gemini

## ข้อมูลทางเทคนิค

- **Image**: `ollama/ollama:latest`
- **Port**: `11434`
- **Volume**: `ollama_data` (เพื่อเก็บโมเดลที่ดาวน์โหลดมา ไม่ให้หายเวลา restart)

## ขั้นตอนการเปลี่ยนแปลง

### [MODIFY] [docker-compose.dev.yml](file:///Users/mpamdev03/projects/python/xInvest/docker-compose.dev.yml)

- เพิ่ม service `ollama`
- ตรวจสอบการเชื่อมต่อเครือข่าย (Network) ให้ backend มองเห็น ollama

### [MODIFY] [requirements.txt](file:///Users/mpamdev03/projects/python/xInvest/backend/requirements.txt)

- เพิ่ม `langchain-ollama` (หากยังไม่มี) เพื่อใช้เชื่อมต่อ

### [MODIFY] [ai_service.py](file:///Users/mpamdev03/projects/python/xInvest/backend/fundDecision/ai_service.py)

- เพิ่ม Logic ในการเรียกใช้ `ChatOllama`
- เพิ่มเงื่อนไขการเลือก LLM ผ่าน Environment Variable (เช่น `AI_PROVIDER=OLLAMA`)

## ตัวอย่างการใช้งานเบื้องหลัง (Proposed Code)

```python
from langchain_ollama import ChatOllama

# ใน SmartFundAIService
self.llm = ChatOllama(
    model="llama3",
    base_url="http://ollama:11434"
)
```
