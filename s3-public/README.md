# AWS Cloud formation template

Run aws cli to install cloud formation template

## install

aws configure


## Create a Stack using AWS CLI

aws cloudformation deploy --template-file infrastructure.yml --stack-name static-website-12345678

## upload files

aws s3 cp chat-react-app/dist s3://bucket-name --recursive

aws s3 cp chat-react-app/dist s3://public-s3-bucket-654599018554 --recursive

## automatic run file using run.bat

run.bat in cmd