#!/bin/bash
set -e

STACK_NAME="URLShortenerService"
HOSTS=""
HARRAY=()
host_num=0

arguments=($@)

input="./nodes"
while read -r line
do
    HOSTS+="$line "
    HARRAY+=($line)
    ((host_num+=1))
done < "$input"

start-stack() {
    cp nodes monitoring/app/nodes

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

reset-cass() {
    echo "Resetting Cassandra data..."
    docker exec cassandra-node cqlsh -f /tmp/schema/reset_table.cql
    docker exec cassandra-node cqlsh -f /tmp/schema/create_keyspace.cql
    docker exec cassandra-node cqlsh -f /tmp/schema/create_table.cql   
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

add-cass() {
    NEW_NODE=${arguments[1]}
    EXISTING_NODE=${arguments[2]}
    COMMAND="docker run --name cassandra-node -d -v /home/student/repo_a2group77/volumes/cassandra/data:/var/lib/cassandra -v /home/student/repo_a2group77/volumes/cassandra/target:/tmp/schema -e CASSANDRA_BROADCAST_ADDRESS=$NEW_NODE -p 7000:7000 -p 9042:9042 -e CASSANDRA_SEEDS=$EXISTING_NODE cassandra"
    exp "hhhhiotwwg" ssh student@$NEW_NODE "docker container stop cassandra-node"
    exp "hhhhiotwwg" ssh student@$NEW_NODE "docker container rm cassandra-node"
    exp "hhhhiotwwg" ssh student@$NEW_NODE "$COMMAND"

    echo "Successfully added $NEW_NODE to cassandra cluster"
}

remove-cass() {
    NODE_TO_REMOVE=${arguments[1]}
    exp "hhhhiotwwg" ssh student@$NODE_TO_REMOVE "docker container stop cassandra-node"
    exp "hhhhiotwwg" ssh student@$NODE_TO_REMOVE "docker container rm cassandra-node"
    line=`docker exec -it cassandra-node nodetool status | grep ${NODE_TO_REMOVE}`
    docker exec -it cassandra-node nodetool removenode `python3 cleanupCassNode.py ${line}`
}

add-node() {
    # Add node to docker swarm
    NEW_NODE=${arguments[1]}
    
    workerJoin=`docker swarm join-token worker | grep token`
    exp "hhhhiotwwg" ssh $NEW_NODE $workerJoin
    
    # Add node to `nodes` file
    echo $NEW_NODE >> nodes
    
    # Scale URL Shortener Service
    let host_num=host_num+1
    docker service scale URLShortenerService_web=$host_num
    curl -X PUT "http://127.0.0.1:5000/?host=$NEW_NODE"
} 

remove-node() {
    EXISTING_NODE=${arguments[1]}
    exp "hhhhiotwwg" ssh $EXISTING_NODE "docker swarm leave --force" || true
    
    # Remove node from 'nodes' file
    sed -i '/EXISTING_NODE/d' nodes
 
    let host_num=host_num-1
    docker service scale URLShortenerService_web=$host_num    
    curl -X DELETE "http://127.0.0.1:5000/?host=$EXISTING_NODE"
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
    add-node)    add-node; print_done ;;
    remove-node) remove-node; print_done ;;
    add-cass)    add-cass; print_done ;;
    remove-cass) remove-cass; print_done ;;
    reset-cass) reset-cass; print_done ;;
    start-stack) start-stack; print_done ;;
    stop-stack) stop-stack; print_done ;;
    start-cass) start-cass; print_done ;;
    stop-cass) stop-cass; print_done ;;
    start-swarm) stop-swarm; start-swarm; print_done ;; 
    leave-swarm) stop-swarm; print_done ;;
    test)     run-test; print_done ;;
    logs)     logs ;;
    *) echo "Usage:"
       echo "  $0 start                            - Start app service"
       echo "  $0 stop                             - Stop all running services"
       echo "  $0 add-node {new_ip}                - Add the new_ip to the swarm and scale the URLShortener service"
       echo "  $0 remove-node {existing_ip}        - Remove the exiting_ip from the swarm, redeploy stack, scale down services"
       echo "  $0 add-cass {new_ip} {existing_ip}  - Adds the new_ip to a cassandra swarm of existing_ip"           
       echo "  $0 remove-cass {ip_to_remove}       - Removes the passed in ip from the cassandra swarm"
       echo "  $0 start-stack                      - Build and start docker stack"
       echo "  $0 stop-stack                       - Stop docker stack"
       echo "  $0 start-cass                       - Start cassandra on all nodes"
       echo "  $0 stop-cass                        - Stop cassandra on all nodes"
       echo "  $0 start-swarm                      - Start swarm on all nodes"
       echo "  $0 leave-swarm                      - Leave swarm on all nodes"
       echo "  $0 test                             - Run tests for both backend and frontend"
       echo "  $0 logs                             - Tail app logs"
       exit 1
       ;;
esac
