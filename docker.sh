docker build -t ada-service-demo .
docker rm -f ada-service-demo
docker run \
    -d \
    --name ada-service-demo \
    -p 8004:8004 \
    --network=ada \
    ada-service-demo
docker logs -f ada-service-demo