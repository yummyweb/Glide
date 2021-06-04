import boto3
import json

# Retrieve the website configuration
s3 = boto3.resource('s3')
_s3 = boto3.client('s3')
s3.create_bucket(
    Bucket="mywebsiteisamazing",
    CreateBucketConfiguration={
        'LocationConstraint': 'ap-south-1'
    }
)

_s3.put_bucket_website(
    Bucket="mywebsiteisamazing",
    WebsiteConfiguration={
     'ErrorDocument': {'Key': 'error.html'},
     'IndexDocument': {'Suffix': 'index.html'},
    }
)

bucket_policy = {
     'Version': '2012-10-17',
     'Statement': [{
         'Sid': 'AddPerm',
         'Effect': 'Allow',
         'Principal': '*',
         'Action': ['s3:GetObject'],
         'Resource': "arn:aws:s3:::%s/*" % "mywebsiteisamazing"
      }]
}
bucket_policy = json.dumps(bucket_policy)


_s3.put_bucket_policy(Bucket='mywebsiteisamazing', Policy=bucket_policy)