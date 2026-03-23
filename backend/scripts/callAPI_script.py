from datetime import datetime, timedelta
import requests
import time

def run_performance_etl(year, month):
    # --- ตั้งค่าตรงนี้ ---
    base_url = "http://localhost:8000"  # เปลี่ยนเป็น URL ของ Server คุณ
    #api_path = "/api/v1/invest/etl/trigger-fconnext-performance-balance/"
    api_path = "/api/v1/invest/etl/trigger-fconnext-transaction/"
    url = f"{base_url}{api_path}"
    token ='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzc0MjQ5ODYxLCJpYXQiOjE3NzQyNDYyNjEsImp0aSI6IjJkNDE0ZjViOTE2ZDQ3MzBiNWIxNjhlMmQ3NWQ2YWViIiwidXNlcl9pZCI6IjEiLCJ1c2VybmFtZSI6InJvb3QiLCJlbWFpbCI6Inl1dHRhbmE3NkBnbWFpbC5jb20iLCJyb2xlIjoiYWRtaW4ifQ.MYi-VEu9meY4YPaaE6UbqXhi1tlqoDAAdenC2KFHCFs'
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}" # ถ้ามี Token ให้เปิดใช้งานบรรทัดนี้
    }

    # คำนวณวันเริ่มต้นและวันสุดท้ายของเดือน
    start_date = datetime(year, month, 1)
    if month == 12:
        next_month = datetime(year + 1, 1, 1)
    else:
        next_month = datetime(year, month + 1, 1)

    current_date = start_date
    print(f"==========================================")
    print(f"🚀 Starting ETL for: {start_date.strftime('%B %Y')}")
    print(f"Target URL: {url}")
    print(f"==========================================")

    while current_date < next_month:
        business_date = current_date.strftime("%Y%m%d")
        payload = {"business_date": business_date}

        try:
            # เพิ่ม timeout=60 เพราะ ETL มักใช้เวลานาน
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            
            if response.status_code in [200, 201]:
                print(f"✅ {business_date}: Success")
            else:
                print(f"❌ {business_date}: Failed (Status: {response.status_code}) - {response.text}")
                
        except requests.exceptions.Timeout:
            print(f"⚠️ {business_date}: Timeout - Server takes too long to respond")
        except Exception as e:
            print(f"⚠️ {business_date}: Error - {str(e)}")

        # ขยับไปวันถัดไป
        current_date += timedelta(days=1)
        
        # หน่วงเวลา 0.5 วินาที เพื่อไม่ให้ยิง Server หนักเกินไป (ปรับตามความเหมาะสม)
        time.sleep(0.5)

    print(f"==========================================")
    print(f"🏁 ETL Process Completed!")
    print(f"==========================================")

# --- ส่วนนี้คือสิ่งที่ทำให้ไฟล์รันได้ ---
if __name__ == "__main__":
    # คุณสามารถเปลี่ยน ปี และ เดือน ที่ต้องการตรงนี้
    TARGET_YEAR = 2026
    TARGET_MONTH = 1
    
    run_performance_etl(TARGET_YEAR, TARGET_MONTH)

    # --- วิธีใช้งาน ---
    #cd ./backend/scripts/
    #python ./backend/scripts/callAPI_script.py
