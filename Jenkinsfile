pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        IMAGE_NAME = 'sim1:latest'
        CONTAINER_NAME = 'sim1'
        DOCKER_NETWORK = 'lee-net'
    }

    stages {
        stage('Build image') {
            steps {
                sh 'docker build --pull -t "$IMAGE_NAME" .'
            }
        }

        stage('Test image') {
            steps {
                sh 'docker run --rm "$IMAGE_NAME" pytest -q'
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    docker network inspect "$DOCKER_NETWORK" >/dev/null
                    docker rm -f "$CONTAINER_NAME" 2>/dev/null || true
                    docker run -d \\
                      --name "$CONTAINER_NAME" \\
                      --restart unless-stopped \\
                      --network "$DOCKER_NETWORK" \\
                      --network-alias sim1 \\
                      --expose 3000 \\
                      "$IMAGE_NAME"
                '''
                sh '''
                    for attempt in $(seq 1 30); do
                      if docker exec "$CONTAINER_NAME" python -c "from urllib.request import urlopen; print(urlopen('http://127.0.0.1:3000/health', timeout=2).read().decode())"; then
                        exit 0
                      fi
                      sleep 2
                    done
                    docker logs "$CONTAINER_NAME"
                    exit 1
                '''
            }
        }
    }

    post {
        failure {
            sh 'docker logs "$CONTAINER_NAME" 2>/dev/null || true'
        }
    }
}
