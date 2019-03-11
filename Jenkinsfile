pipeline {
    agent { 
        node {label 'bare-metal' }
    } 
    stages {
        stage('Build') { 
            steps {
                // Build container
                sh 'echo Build shock server'
                sh 'docker build -t shock:testing .' 
                sh 'echo Build test client'
                sh 'docker build -t shock-test-client:testing -f test/Dockerfile .'
            }
        }
        stage('Setup') {
            steps {
                // Create network
                sh 'docker network create shock-test'
                // start services
                sh 'docker run -d --rm --network shock-test --name shock-server-mongodb --expose=27017 mongo mongod --dbpath /data/db'
                sh 'docker run -d --rm --network shock-test --name shock-server -p 7445:7445 shock:testing /go/bin/shock-server --hosts shock-server-mongodb'
            }
        }
        stage('Test') { 
            steps {
                // execute tests
                sh 'docker run -t --rm --network shock-test shock-test-client:testing  /shock-tester.sh -h http://shock-server -p 7445'
                sh '''docker run -t --rm --network shock-test --env SHOCK_HOST="http://shock-server" --env SHOCK_PORT=7445 mgrast/shock-test-client:testing \
                    qpytest /go/src/github.com/MG-RAST/Shock/test/test_shock.py  -h http://shock-server -p 7445'''
            }   
        }
    }
    post {
        always {
             // shutdown container and network
                sh 'docker stop shock-server shock-server-mongodb'
                sh 'docker rmi shock:testing shock-test-client:testing'
                sh 'docker network rm shock-test'
                // delete images
        }
    }
}
