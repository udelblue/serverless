@echo off
REM Deploy the CloudFormation stack
echo Deploying CloudFormation stack...
aws cloudformation deploy --template-file infrastructure.yml --stack-name static-website-12345678
if %ERRORLEVEL% neq 0 (
    echo Failed to deploy CloudFormation stack.
    exit /b %ERRORLEVEL%
)

REM Retrieve the bucket name from the stack outputs
echo Retrieving bucket name...
for /f "tokens=*" %%i in ('aws cloudformation describe-stacks --stack-name static-website-12345678 --query "Stacks[0].Outputs[?OutputKey=='BucketName'].OutputValue" --output text') do set BUCKET_NAME=%%i

REM Check if the bucket name was retrieved
if "%BUCKET_NAME%"=="" (
    echo Failed to retrieve bucket name.
    exit /b 1
)

REM Replace bucket-name and upload files to the bucket
echo Uploading files to bucket: %BUCKET_NAME%...
aws s3 cp chat-react-app/dist s3://%BUCKET_NAME% --recursive
if %ERRORLEVEL% neq 0 (
    echo Failed to upload files to S3 bucket.
    exit /b %ERRORLEVEL%
)

echo Files successfully uploaded to bucket: %BUCKET_NAME%.