# Library updates check
In this project we can check the version of Python libraries, and send notification automatically if there are any updates to registered users by email.
This project is built with the use of python, celery, reddis, beat, fastapi, mongodb.

## Build Docker containers
```bash
docker-compose up --build
```

## Access mongodb and interaction with it
```bash
# access db to see and choose databas, and see users in it
docker compose exec mongo mongosh 
```
The following are the MongoDB query language commands that should be run after we entered the mongo.
```
show dbs
```
```
use fastapi_db
```
```
show collections
```
```
db.users.find().pretty()
```
```
exit
```

## Add user
```bash
curl -X POST "http://localhost:8000/submit/" -H "Content-Type: application/json" -d '{
           "name": "UserName",
           "password": "securepassword",
           "email": "user@example.com"
           }'
```

## Add libraries
```bash
curl -X PUT "http://localhost:8000/users/user@example.com/libraries/" -H "Content-Type: application/json" -d '{"libraries": ["motor", "pandas"]}'
```

## Get user
```bash
curl -X GET "http://localhost:8000/users/user@example.com" 
```

## Change versions of python libraries via database
```bash
# This code should be run inside the database
db.users.updateOne(
    { "email": "user@example.com" },  
    { "$set": { "libraries.motor": "3.8.0", "libraries.pandas": "2.2.2"
    } 
    } 
) 
```
<!-- db.users.updateOne(
    { "email": "maria.parfenchyk@gmail.com" },  
    { "$set": { "libraries.seaborn": "0.13.0", "libraries.numpy": "2.2.2"
    } 
    } 
) -->

