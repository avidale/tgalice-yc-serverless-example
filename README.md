

make all
# upload dist.zip
yc serverless function version create
    --function-name=horoscope
    --environment=k1=v1,AWS_ACCESS_KEY_ID={KEY ID},AWS_SECRET_ACCESS_KEY={KEY VALUE}
    --runtime=python37
    --package-bucket-name=firstbucket
    --package-object-name=dist.zip
    --entrypoint=main.alice_handler
    --memory=128M
    --execution-timeout=3s
