pipeline {
  agent any

  environment {
    VENV = ".venv"
    APP_NAME = "giftshop"
    APP_HOST = "13.201.84.211"   // 🔹 replace with your server IP or DNS
    APP_DIR  = "/opt/giftshop"
    SSH_CRED = "deploy_ssh"                 // 🔹 Jenkins Credentials ID (SSH key)
  }

  options {
    timestamps()
    ansiColor('xterm')
  }

  stages {
    stage('Checkout') {
      steps {
        deleteDir()
        checkout scm
      }
    }

    stage('Install dependencies') {
      steps {
        sh '''
          python3 -m venv ${VENV}
          . ${VENV}/bin/activate
          pip install --upgrade pip
          pip install -r requirements.txt
        '''
      }
    }

    stage('Run tests') {
      steps {
        sh '''
          . ${VENV}/bin/activate
          pytest -q
        '''
      }
    }

    stage('Package app') {
      steps {
        sh '''
          tar czf ${APP_NAME}.tar.gz app.py requirements.txt templates static
        '''
        archiveArtifacts artifacts: "${APP_NAME}.tar.gz", fingerprint: true
      }
    }

    stage('Deploy to server') {
      steps {
        sshagent (credentials: [env.SSH_CRED]) {
          sh '''
            # Copy tarball to server
            scp -o StrictHostKeyChecking=no ${APP_NAME}.tar.gz ${APP_HOST}:/tmp/${APP_NAME}.tar.gz

            # Deploy remotely
            ssh -o StrictHostKeyChecking=no ${APP_HOST} bash -lc '
              set -e
              sudo mkdir -p ${APP_DIR}
              sudo tar xzf /tmp/${APP_NAME}.tar.gz -C ${APP_DIR} --overwrite
              cd ${APP_DIR}
              python3 -m venv .venv
              . .venv/bin/activate
              pip install --upgrade pip
              pip install -r requirements.txt

              # Systemd unit file for Gunicorn
              sudo bash -c "cat > /etc/systemd/system/${APP_NAME}.service" <<EOF
[Unit]
Description=Gift Shop Flask (Gunicorn)
After=network.target

[Service]
User=$(whoami)
WorkingDirectory=${APP_DIR}
ExecStart=${APP_DIR}/.venv/bin/gunicorn -b 0.0.0.0:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

              sudo systemctl daemon-reload
              sudo systemctl enable ${APP_NAME}
              sudo systemctl restart ${APP_NAME}
            '
          '''
        }
      }
    }
  }

  post {
    success {
      echo "✅ Deployed successfully → http://${env.APP_HOST}:5000/"
    }
    failure {
      echo "❌ Build/Deploy failed"
    }
  }
}
