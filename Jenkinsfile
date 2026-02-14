pipeline {
    agent any

    environment {
        Docker_Credentials = credentials('sanju1701')
        Docker_Image = "sanju1701/chatbot"
    }

    stages {

        stage('Checkout Code') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/Sanjeevan-17/Chatbot.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build -t $Docker_Image:latest .
                    docker tag $Docker_Image:latest $Docker_Image:$BUILD_NUMBER
                '''
            }
        }

        stage('Push Docker Image') {
            steps {
                sh '''
                    echo $Docker_Credentials_PSW | docker login -u $Docker_Credentials_USR --password-stdin
                    docker push $Docker_Image:latest
                    docker push $Docker_Image:$BUILD_NUMBER
                '''
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    docker pull $Docker_Image:latest
                    docker stop chatbot || true
                    docker rm chatbot || true
                    docker run -d -p 8070:5000 --name chatbot $Docker_Image:latest

                '''
            }
        }
    }

    post {
        success {
            echo '✅ Build, Test, Push, Deploy completed successfully!'
        }
        failure {
            echo '❌ Pipeline failed. Check logs.'
        }
    }
}
