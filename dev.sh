#!/bin/bash
set -e

STACK_NAME="URLShortenerService"
HOSTS=""
HARRAY=()

input="./nodes"
while read -r line
do
    HOSTS+="$line "
    HARRAY+=($line)
done < "$input"


start-stack() {
    echo "Building images..."
    cd databaseUpdater
    docker build -t georgema8/databaseupdater:v1 .
    cd ..
    cd monitoring
    docker build -t georgema8/monitorstatus:v1 .
    cd ..
    docker build -t georgema8/urlshortner:v1 .
    echo "Pushing images to cassandra..."
    docker push georgema8/databaseupdater:v1
    docker push georgema8/urlshortner:v1
    docker push georgema8/monitorstatus:v1

    docker stack deploy -c docker-compose.yml $STACK_NAME
}

stop-stack() {
    echo "TODO: Catch when the stack is not already up"
    docker stack rm $STACK_NAME
}

start-cass() {
    echo "Starting Cassandra..."
    ./startCluster ${HOSTS}
    docker exec cassandra-node cqlsh -f /tmp/schema/create_keyspace.cql
    docker exec cassandra-node cqlsh -f /tmp/schema/create_table.cql
}

stop-cass() {
    echo "Stopping Cassandra..."
    ./stopCluster ${HOSTS}
}

start-swarm() {
    echo "Initializing swarm..."
    docker swarm init --advertise-addr ${HARRAY[0]}
    
    workerJoin=`docker swarm join-token worker | grep token`
    
    echo "Joining swarm on worker nodes..."
    for i in "${HARRAY[@]:1}"
    do
        exp "hhhhiotwwg" ssh $i $workerJoin
    done
    # SSH leave and join on the other nodes
}

stop-swarm() {
    for i in "${HARRAY[@]}"
    do
        exp "hhhhiotwwg" ssh $i "docker swarm leave --force" || true 
    done
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
    start)    start-cass; start-swarm; start-stack; print_done ;;
    stop)     stop-stack; stop-cass; stop-swarm; print_done ;;
    start-stack) start-stack ;;
    stop-stack) stop-stack ;;
    start-cass) start-cass ;;
    stop-cass) stop-cass ;;
    start-swarm) stop-swarm; start-swarm ;;
    leave-swarm) stop-swarm ;;
    test)     run-test; print_done ;;
    logs)     logs ;;
    *) echo "Usage:"
       echo "  $0 start      - Start app service"
       echo "  $0 stop       - Stop all running services"
       echo "  $0 start-stack        - Build and start docker stack"
       echo "  $0 stop-stack         - Stop docker stack"
       echo "  $0 start-cass         - Start cassandra on all nodes"
       echo "  $0 stop-cass          - Stop cassandra on all nodes"
       echo "  $0 start-swarm        - Start swarm on all nodes"
       echo "  $0 leave-swarm        - Leave swarm on all nodes"
       echo "  $0 test       - Run tests for both backend and frontend"
       echo "  $0 logs       - Tail app logs"
       exit 1
       ;;
esac
