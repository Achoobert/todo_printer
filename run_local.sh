

docker container stop $(docker container ls | grep "todo")
docker container rm $(docker container ls | grep "todo")

docker build -t digiserve/todo-printer .

docker compose up -d 

sleep 10
docker logs todo_printer-todo-printer-1