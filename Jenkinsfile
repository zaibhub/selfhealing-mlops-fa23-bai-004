pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-creds')
        IMAGE_UNSTABLE = "alizaibdocker/sentiment-api:unstable"
        IMAGE_STABLE = "alizaibdocker/sentiment-api:stable"
    }

    stages {
        stage('Fetch') {
            steps {
                checkout scm
            }
        }

        stage('Build and Run') {
            steps {
                sh '''
                    docker build -t sentiment-api:unstable-test .
                    docker rm -f sentiment-test || true
                    docker run -d --name sentiment-test -p 5001:5000 sentiment-api:unstable-test
                    sleep 30
                '''
            }
        }

        stage('Unit Test') {
            steps {
                sh '''
                    docker exec sentiment-test pip install pytest requests
                    docker exec -e BASE_URL=http://localhost:5000 sentiment-test python -m pytest tests/test_api.py -v
                '''
            }
        }

        stage('UI Test') {
            steps {
                sh '''
                    docker run --rm --network container:sentiment-test \
                        -v jenkins_home:/workspace_data \
                        -w /workspace_data/workspace/sentiment-ci-pipeline \
                        -e BASE_URL=http://localhost:5000 \
                        -e HOME=/tmp \
                        selenium/standalone-chrome:latest \
                        bash -c "pip3 install selenium pytest requests --break-system-packages --user 2>/dev/null || pip3 install selenium pytest requests --break-system-packages; python3 -m pytest tests/test_ui.py -v -p no:cacheprovider"
                '''
            }
        }

        stage('Build and Push') {
            steps {
                sh '''
                    docker tag sentiment-api:unstable-test $IMAGE_UNSTABLE
                    echo $DOCKERHUB_CREDENTIALS_PSW | docker login -u $DOCKERHUB_CREDENTIALS_USR --password-stdin
                    docker push $IMAGE_UNSTABLE

                    git fetch origin stable-fallback
                    git checkout origin/stable-fallback -- .
                    docker build -t $IMAGE_STABLE .
                    docker push $IMAGE_STABLE

                    git checkout .
                '''
            }
        }

        stage('Deploy to Minikube') {
            steps {
                sh '''
                    kubectl apply -f k8s/pvc.yaml
                    kubectl apply -f k8s/blue-deployment.yaml
                    kubectl apply -f k8s/green-deployment.yaml
                    kubectl apply -f k8s/service.yaml
                '''
            }
        }
    }

    post {
        always {
            sh '''
                docker rm -f sentiment-test || true
                docker rmi sentiment-api:unstable-test || true
                docker rmi $IMAGE_UNSTABLE || true
                docker rmi $IMAGE_STABLE || true
                docker image prune -f || true
                docker builder prune -f || true
            '''
        }
    }
}
