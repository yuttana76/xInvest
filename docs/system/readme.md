# Initial project

```
docker compose up -d --build
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py collectstatic --noinput
```

## Create super user

docker compose exec backend python manage.py createsuperuser

Groups
operator
marketing
agent

      role: 'admin' | 'investor' | 'operator' | 'marketing' | 'agent' | 'guest';

You can verify the pages at:
Investor: http://localhost/dashboard
Admin: http://localhost/admin-portal
Django: http://localhost/admin/

# How to Start the Development Stack

## docker remove image<none>

docker rmi $(docker images -f "dangling=true" -q)

To start the services in development mode, use the following command:

docker compose -f docker-compose.dev.yml up -d --build
docker compose -f docker-compose.dev.yml up -d
docker compose -f docker-compose.dev.yml down

## backend

docker exec -it xinvest-backend-1 sh
docker exec -it xinvest-backend-1 python manage.py makemigrations
docker exec -it xinvest-backend-1 python manage.py migrate

docker stop xinvest-backend-1

docker restart xinvest-backend-1

docker logs -f xinvest-backend-1

docker logs -f xinvest-celery_worker-1

docker exec -it xinvest-backend-1 sh

docker compose -f docker-compose.dev.yml up -d --build backend
docker compose -f docker-compose.dev.yml up -d backend

## frontend

docker stop xinvest-frontend-1
docker compose -f docker-compose.dev.yml up -d --build frontend

## go-trading

docker compose -f docker-compose.dev-trade.yml up -d --build
docker compose -f docker-compose.dev-trade.yml up -d
docker compose -f docker-compose.dev-trade.yml down

docker restart xinvest-go_trading-1
docker stop xinvest-go_trading-1
docker logs -f xinvest-go_trading-1

docker compose -f docker-compose.dev-trade.yml up -d --build go_trading
docker compose -f docker-compose.dev-trade.yml up -d go_trading

## Mobile

Test in Browser (Chrome)

```
cd x_mobile_app
flutter run -d chrome
```

Test as macOS App

```
cd x_mobile_app
flutter run -d macos
```

2. Verify Health

curl http://localhost:8080/health

http://localhost:8080/api/v1/invesInfo

## Celery-Worker

docker restart xinvest-celery_worker-1
docker logs -f xinvest-celery_worker-1

docker stop xinvest-celery_worker-1
docker compose -f docker-compose.dev.yml up -d celery_worker

docker stop xinvest-celery_worker-1 xinvest-celery_beat-1
docker compose -f docker-compose.dev.yml up -d --build celery_worker celery_beat

docker stop xinvest-celery_worker-1 xinvest-backend-1
docker compose -f docker-compose.dev.yml up -d celery_worker backend

Access Points
Django Backend: http://localhost:8000
Next.js Frontend: http://localhost:3000
PostgREST API: http://localhost:3001
Celery Flower: http://localhost:5555/tasks

PostgreSQL: localhost:5432
Redis: localhost:6379
Next Steps for You
To start everything with the new settings:

bash
docker compose up -d --build
PostgREST will be available at http://localhost:3001 and your Django API at http://localhost:8000.

## RAG

python lib

> psycopg2-binary sentence-transformers

## Ollama

https://ollama.com/library

> docker exec -it xinvest-ollama-1 sh

> docker logs -f xinvest-ollama-1

> docker logs xinvest-ollama-1 --tail 50

ดาวน์โหลดโมเดลมาเก็บไว้ (แต่ยังไม่เริ่มรัน)

> ollama pull llama3

ollama run <name>
/bye: ออกจากการแชท (Exit)
/?: ดูคำสั่งช่วยเหลือทั้งหมด
/set verbose: สั่งให้แสดงความเร็วในการประมวลผล (Tokens per second) หลังตอบเสร็จ

> docker exec -it xinvest-ollama-1 ollama list
> docker exec -it xinvest-ollama-1 ollama rm <name>

เปลี่ยนไปใช้โมเดลที่ตัวเล็กกว่าและกินแรมน้อยกว่า
หากเครื่อง Mac ของคุณมีแรมจำกัดและไม่อยากเพิ่มให้ Docker คุณสามารถสลับไปรันโมเดลที่เล็กลง เช่น phi3 (กินแรมแค่ประมาณ 2.3 GB) หรือ llama3.2:1b (กินเพียง 1.3 GB) แทนได้

- เปิดไฟล์ .env.dev หาบรรทัด OLLAMA_MODEL=llama3
- เปลี่ยนเป็น OLLAMA_MODEL=phi3
- สั่งโหลดโมเดลเล็กด้วยคำสั่ง docker exec -it xinvest-ollama-1 ollama pull phi3 (รันแปปเดียวเสร็จ)
- Restart ตัว backend เพื่อให้มันโหลด .env ใหม่ด้วยคำสั่ง docker restart xinvest-backend-1

## GraphQL

http://localhost:8000/graphql

query {
fundProfileByCode(fundCode: "KT-OIL") {
fundCode
fundNameEn
fundNameTh
fundRiskLevel
dividendFlag
fundAnalysis {
sentimentScore
sentimentSummary
standardDeviation
lastCalculated
}
}
}
