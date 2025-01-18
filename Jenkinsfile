pipeline {
  agent any
  stages {
    stage('Checkout Code') {
      steps {
        git(url: 'https://github.com/nn-develop/CryptoBot', branch: 'main')
      }
    }

    stage('Just log') {
      steps {
        sh 'ls -la'
      }
    }

  }
}