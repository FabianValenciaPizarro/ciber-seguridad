pipeline {
agent any

environment {
    APP_NAME = "securedev-app"
    CONTAINER_NAME = "app-prod"
    NETWORK_NAME = "devsecops-net"
}

stages {
    stage('1. Construccion (Build)') {
        steps {
            echo 'Construyendo imagen Docker de la aplicacion...'
            sh 'docker build -t securedev-app:latest .'
        }
    }

    stage('2. Revision Estatica de Codigo (SAST)') {
        steps {
            echo 'Ejecutando analisis estatico de seguridad (Bandit)...'
            sh 'docker run --rm -v "$(pwd)":/src python:3.9-slim bash -c "pip install -q bandit && bandit -r /src/app.py || true"'
        }
    }

    stage('3. Despliegue (Deploy)') {
        steps {
            echo 'Desplegando contenedor en red de produccion...'
            sh '''
                docker stop app-prod || true
                docker rm app-prod || true
                docker run -d --name app-prod --network devsecops-net -p 5000:5000 securedev-app:latest
                sleep 5
            '''
        }
    }

    stage('4. Pruebas Automatizadas de Seguridad (OWASP ZAP)') {
        steps {
            echo 'Ejecutando escaneo DAST con OWASP ZAP contra el entorno desplegado...'
            sh '''
                mkdir -p zap-reports
                chmod 777 zap-reports
                docker run --rm --user 0:0 --network devsecops-net \
                    -v "$(pwd)/zap-reports:/zap/wrk/:rw" \
                    ghcr.io/zaproxy/zaproxy:stable zap-baseline.py \
                    -t http://app-prod:5000 \
                    -r zap_report.html || true
                ls -la zap-reports
            '''
        }
    }
}

post {
    always {
        archiveArtifacts artifacts: 'zap-reports/zap_report.html', allowEmptyArchive: true
        echo 'Pipeline finalizado. Reporte OWASP ZAP archivado.'
    }
}
}
