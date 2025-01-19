pipeline {
  agent any
  stages {
    stage('Checkout Code') {
      steps {
        git(url: 'https://github.com/nn-develop/CryptoBot', branch: 'main')
      }
    }

    stage('Install Requirements') {
      steps {
        sh 'pip3 install -r requirements-dev.txt'
      }
    }

    stage('Parallel Tasks') {
      parallel {
        stage('Just log') {
          steps {
            sh 'ls -la'
          }
        }
        stage('Run Tests') {
          steps {
            sh 'python3 -m unittest discover -s tests > test_results'
          }
        }
      }
    }
  }
}
