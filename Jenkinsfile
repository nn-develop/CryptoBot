pipeline {
  agent any
  stages {
    stage('Checkout Code') {
      steps {
        git(url: 'https://github.com/nn-develop/CryptoBot', branch: 'main')
      }
    }

    stage('Install Python') {
      steps {
        sh 'sudo apt-get update && sudo apt-get install -y python3 python3-pip'
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
