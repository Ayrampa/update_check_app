# Acces mongodb
docker compose exec mongo mongosh
show dbs # show list of databases
use mydatabase
show collections
db.users.find().pretty()
exit



# Directly query MongoDB from outside the container
docker compose exec mongo mongosh mydatabase --eval "db.users.find().pretty()"


http://localhost:8000/users/?name=Ann&email=ann@example.com&libraries=pandas&libraries=numpy



# Add libraries
curl -X PUT "http://localhost:8000/users/lmb11@example.com/libraries/" -H "Content-Type: application/json" -d '{"libraries": ["motor", "pandas", "seaborned", "celery"]}'


# Add user
curl -X POST "http://localhost:8000/submit/" -H "Content-Type: application/json" -d '{
           "name": "Lmb11",
           "password": "securepassword9",
           "email": "lmb11@example.com"
           }'

# Get user
curl -X GET "http://localhost:8000/users/lmb11@example.com" 

pip3 freeze > requirements.txt

# Add myself
curl -X POST "http://localhost:8000/submit/" -H "Content-Type: application/json" -d '{
           "name": "Mary",
           "password": "securepassword10",
           "email": "maria.parfenchyk@gmail.com"
           }'


curl -X PUT "http://localhost:8000/users/maria.parfenchyk@gmail.com/libraries/" -H "Content-Type: application/json" -d '{"libraries": ["motor", "pandas"]}'

db.users.updateOne(
    { "email": "maria.parfenchyk@gmail.com" },  
    { "$set": { "libraries.motor": "3.8.0", "libraries.pandas": "2.2.2" } } 
) 

docker exec -it update_check_app_celery-beat_1 sh
celery -A tasks beat --scheduler celery.beat.schedulers.PersistentScheduler --loglevel=info

