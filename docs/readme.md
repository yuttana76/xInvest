# Initial project

```
docker compose up -d --build
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py collectstatic --noinput
```

## Create super user

docker compose exec backend python manage.py createsuperuser

Users
root:Mps@2026

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
docker exec -it xinvest-backend-1 sh

docker compose -f docker-compose.dev.yml up -d --build backend

## go-trading

docker compose -f docker-compose.dev-trade.yml up -d --build
docker compose -f docker-compose.dev-trade.yml up -d
docker compose -f docker-compose.dev-trade.yml down

docker restart xinvest-go_trading-1
docker stop xinvest-go_trading-1
docker logs -f xinvest-go_trading-1

docker compose -f docker-compose.dev-trade.yml up -d --build go_trading

2. Verify Health

curl http://localhost:8080/health

http://localhost:8080/api/v1/invesInfo

## Celery-Worker

docker restart xinvest-celery_worker-1
docker logs -f xinvest-celery_worker-1

docker stop xinvest-celery_worker-1 xinvest-celery_beat-1
docker compose -f docker-compose.dev.yml up -d --build celery_worker celery_beat

docker stop xinvest-celery_worker-1 xinvest-celery_beat-1 xinvest-backend-1

docker compose -f docker-compose.dev.yml up -d --build celery_worker celery_beat backend

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

## Create virtual environment

bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip list

## Deactivate virtual environment

> deactivate
