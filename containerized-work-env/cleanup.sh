docker rm -f \
  containerized-work-env-personal.stage-0 \
  containerized-work-env-personal

docker container prune

docker image prune -a
