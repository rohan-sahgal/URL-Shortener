#!/bin/bash
set -e

#HOSTS="10.11.12.17 10.11.12.18 10.11.12.19 10.11.12.231 10.11.12.232"
HOSTS=""

input="./nodes"
while read -r line
do
    echo "$line"
done < "$input"

start() {
    echo "Bringing up Docker containers..."
    ./startCluster ${HOSTS}
}

stop() {
    echo "Stopping and removing Docker containers..."
    ./stopCluster ${HOSTS}
    #docker stack rm 
}

start-swarm() {
    # leave on the host node
    # init on host node (somehow save that output of docker swarm join...)
    echo "hello"
    # SSH leave and join on the other nodes
}

leave-swarm() {
    ssh 10.11.12.17 "docker swarm leave --force"
}

run-test() {
    echo "Run python testing files..."
}


logs() {
    docker container ls
}

print_done() {
    echo "Done."
}

case "$1" in
    start)    start; print_done ;;
    stop)     stop; print_done ;;
    leave-swarm) leave-swarm ;;
    test)     run-test; print_done ;;
    logs)     logs ;;
    *) echo "Usage:"
       echo "  $0 start      - Start app service"
       echo "  $0 stop       - Stop all running services"
       echo "  $0 leave-swarm        - Leave swarm on all nodes"
       echo "  $0 test       - Run tests for both backend and frontend"
       echo "  $0 logs       - Tail app logs"
       exit 1
       ;;
esac
