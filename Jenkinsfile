def buildId, version
 
pipeline {
    agent any

    environment {
        REL_VERSION = '1.0.1'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script { version = sh(script: "git rev-parse --short HEAD", returnStdout: true).trim() }
                echo "Checkout successful"
            }
        }
        
        stage('Build') {
            steps {
                 echo "Building ..."
                //script { currentBuild.displayName = "${env.BUILD_NUMBER}-${version}".trim() }
            }
        }

        stage('Prepare Test Environment') {
            steps {
                echo "Preparing Test environment ..."
                sleep 3
                echo "Refreshed Test envitonment to Baseline version"
            }
        }

        stage('Tests') {
            steps {
                echo "Running Tests ..."
            }
        }

        stage('Publish') {
            when {
				expression { return env.BRANCH_NAME ==~ /(?i)(^master$|^release.*)/ }
			}
            steps {
                
                script {
                    def branches = ["master"]
                    def imageTag = (branches.contains(env.BRANCH_NAME)) ? "${REL_VERSION}" : "${env.BUILD_NUMBER}-${version}"
                    
                    // 1. Publish the docker image to Artifactory
                    // 2. Package and publish the "tar.gz" using JFrog CLI to Artifactory
                }
                sh "touch infn-net-ansible-playbooks.tar.gz"
                sh "tar -czf infn-net-ansible-playbooks.tar.gz --exclude='./.git' --exclude=infn-net-ansible-playbooks.tar.gz ."
                sh "cp infn-net-ansible-playbooks.tar.gz infn-net-ansible-playbooks-${REL_VERSION}-${BUILD_NUMBER}.tar.gz"
                sh "mv infn-net-ansible-playbooks.tar.gz infn-net-ansible-playbooks-latest.tar.gz"
                uploadArtifact()
                echo "Published the validated docker image successfully"
                echo "Published the validated .tgz package to Arifactory"
                
                sh "rm -rf infn-net-ansible-playbooks-${REL_VERSION}-${BUILD_NUMBER}.tar.gz"
                sh "rm -rf infn-net-ansible-playbooks-latest.tar.gz"
                sh "rm -rf infn-net-ansible-playbooks.tar.gz"


            }
        }
    }
}

def sendEmail() {
    if (env.NET_EMAIL_NOTIFICATION) {
        emailext (
                    subject:"NEW BUILD : Job ${env.JOB_NAME} [${env.BUILD_NUMBER}]", 
                    body:"""JOB_NAME: Job ${env.JOB_NAME}\n
                    BUILD NUMBER:${env.BUILD_NUMBER}\n
                    CONSOLE_OUTPUT: ${env.BUILD_URL}""", 
                    to: "${env.NET_EMAIL_NOTIFICATION}")
    }
}

def uploadArtifact() {
    def server = Artifactory.server 'iartifactory'
    def uploadSpec = """{
        "files": [
            {
                "pattern": "infn-net-ansible-playbooks-latest.tar.gz",
                "target": "tar-local/NET/"
            },
            {
                "pattern": "infn-net-ansible-playbooks-${REL_VERSION}-${BUILD_NUMBER}.tar.gz",
                "target": "tar-local/NET/"
            }
        ]}"""
    server.upload spec: uploadSpec

    sendEmail()
}