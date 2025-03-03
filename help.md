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
curl -X PUT "http://localhost:8000/users/john@example.com/libraries/" \
     -H "Content-Type: application/json" \
     -d '{
           "libraries": ["pydantic", "motor"]
         }'


