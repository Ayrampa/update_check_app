pip install fastapi uvicorn pymongo motor aiohttp celery redis smtplib python-dotenv




curl -X POST "http://localhost:8000/subscribe/" -H "Content-Type: application/json" -d '{
  "email": "user@example.com",
  "libraries": ["fastapi", "pydantic"]
}'


curl -X PUT "http://localhost:8000/user/user@example.com/add/" -H "Content-Type: application/json" -d '["numpy", "requests"]'


broker_connection_retry_on_startup = True.

pip install fastapi uvicorn motor pymongo celery redis requests smtplib python-dotenv celery[beat]

docker-compose up --build

curl -X POST "http://localhost:8000/users/" -H "Content-Type: application/json" \
     -d '{"name": "John Doe", "email": "john@example.com", "libraries": ["fastapi", "pydantic"]}'

     curl -X POST "http://localhost:8000/check-updates/"




     docker compose exec mongo
     