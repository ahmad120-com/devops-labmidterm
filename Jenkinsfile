// CSC418 Lab Midterm - Muhammad Ahmad (FA23-BDS-048)
pipeline {
    agent any
    options {
        skipDefaultCheckout(true)
        disableConcurrentBuilds()
        timeout(time: 15, unit: 'MINUTES')
    }
    triggers {
        githubPush()
    }
    environment {
        STUDENT_ID = 'FA23-BDS-048'
        IMAGE      = 'midterm-fa23-bds-048'
        CONTAINER  = 'midterm-app'
        APP_URL    = 'http://52.64.85.224:8000'
        NOTIFY_TO  = 'qasimalik@gmail.com, ahmadkhang505@gmail.com'
        SENDER     = 'ahmadkhang505@gmail.com'
    }
    stages {
        stage('Fetch latest data') {
            steps {
                checkout scm
                script { env.GIT_SHA = sh(script: 'git rev-parse HEAD', returnStdout: true).trim() }
                sh 'echo "Commit: ${GIT_SHA}"; echo "Dataset lines: $(wc -l < dataset/train.csv)"'
            }
        }
        stage('Build environment') {
            steps { sh 'docker build --target deps -t ${IMAGE}:deps .' }
        }
        stage('Retrain model') {
            steps {
                sh 'rm -rf artifacts'
                sh 'docker run --rm -u $(id -u):$(id -g) -e GIT_COMMIT=${GIT_SHA} -v "$WORKSPACE":/app -w /app ${IMAGE}:deps python train.py'
            }
        }
        stage('Run tests') {
            steps {
                sh 'docker run --rm -u $(id -u):$(id -g) -v "$WORKSPACE":/app -w /app ${IMAGE}:deps python -m pytest -q -p no:cacheprovider tests'
            }
        }
        stage('Build Docker image') {
            steps { sh 'docker build --target app -t ${IMAGE}:${BUILD_NUMBER} -t ${IMAGE}:latest .' }
        }
        stage('Deploy on EC2') {
            steps {
                sh '''
                    docker rm -f ${CONTAINER} || true
                    docker run -d --name ${CONTAINER} --restart unless-stopped -p 8000:8000 ${IMAGE}:${BUILD_NUMBER}
                '''
            }
        }
        stage('Verify deployment') {
            steps {
                sh '''
                    for i in $(seq 1 30); do
                        if curl -fs http://localhost:8000/metrics | grep -q "${GIT_SHA}"; then
                            curl -s http://localhost:8000/metrics; echo; exit 0
                        fi
                        sleep 2
                    done
                    docker logs --tail 50 ${CONTAINER}; exit 1
                '''
            }
        }
    }
    post {
        always {
            script {
                def metrics = sh(script: 'cat artifacts/metrics.json 2>/dev/null || echo "not available"', returnStdout: true).trim()
                emailext(
                    to: env.NOTIFY_TO,
                    from: env.SENDER,
                    subject: "${env.STUDENT_ID} - MIDTERM build #${env.BUILD_NUMBER}: ${currentBuild.currentResult}",
                    mimeType: 'text/html',
                    body: """
                        <p><b>Student Reg No:</b> ${env.STUDENT_ID}</p>
                        <p><b>Result:</b> ${currentBuild.currentResult}</p>
                        <p><b>Job:</b> ${env.JOB_NAME} #${env.BUILD_NUMBER}</p>
                        <p><b>Commit:</b> ${env.GIT_SHA}</p>
                        <p><b>Metrics:</b> <a href="${env.APP_URL}/metrics">${env.APP_URL}/metrics</a></p>
                        <pre>${metrics}</pre>
                    """
                )
            }
        }
    }
}
