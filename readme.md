```
docker compose up -d --build
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py collectstatic --noinput
```

You can verify the pages at:
Investor: http://localhost/dashboard
Admin: http://localhost/admin-portal
Django: http://localhost/admin/

# How to Start the Development Stack

## docker remove image<none>

docker rmi $(docker images -f "dangling=true" -q)

To start the services in development mode, use the following command:

## docker command

bash
docker compose -f docker-compose.dev.yml up -d --build
docker compose -f docker-compose.dev.yml up -d
docker compose -f docker-compose.dev.yml down
docker exec xinvest-backend-1 python manage.py migrate

docker stop xinvest-backend-1
docker compose -f docker-compose.dev.yml up -d --build backend

docker exec -it xinvest-backend-1 python manage.py makemigrations
docker exec -it xinvest-backend-1 python manage.py migrate

docker logs -f xinvest-backend-1

Access Points
Django Backend: http://localhost:8000
Next.js Frontend: http://localhost:3000
PostgREST API: http://localhost:3001
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
