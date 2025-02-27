pip install fastapi uvicorn pymongo motor aiohttp celery redis smtplib python-dotenv

curl -X POST "http://localhost:8000/subscribe/" -H "Content-Type: application/json" -d '{
  "email": "user@example.com",
  "libraries": ["fastapi", "pydantic"]
}'


curl -X PUT "http://localhost:8000/user/user@example.com/add/" -H "Content-Type: application/json" -d '["numpy", "requests"]'
