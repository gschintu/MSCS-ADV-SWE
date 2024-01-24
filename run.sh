docker build -t flaskstock .

docker run -d -p 8080:8080 --name flaskstock  flaskstock

#gcloud init
#gcloud config set project <project_id>