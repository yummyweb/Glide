import hashlib
import boto3
import sys
import requests
import os
import json
import time
from botocore.exceptions import ClientError
from src.utils import err

class Api:
    def __init__(self, projectName):
        self.projectName = projectName
        self.netlifyBaseUrl = 'https://api.netlify.com/api/v1'
        self.vercelBaseUrl = 'https://api.vercel.com'

    def getConfig(self) -> dict:
        """
        Reads the config file and returns the file contents as dict
        """
        try:
            f = open(self.projectName + ".glide.json", "r")
        except:
            err("ERROR: Glide file does not exist. Please run init command.")
            sys.exit(1)
            

        return json.loads(f.read())

    def getAWSConfig(self):
        """
        Reads the config file and returns AWS config
        """
        config = self.getConfig()
        return (config['access_token'], config['access_secret'], config['region'])

    def getAccessToken(self) -> tuple:
        """
        Gets the config file and returns the access token
        """
        config = self.getConfig()
        if config['access_token']:
            return (config['access_token'])
        else:
            err("Access token not specified. Please provide the access token from your cloud provider.")
            sys.exit(1)
            
    
    def getHeaders(self, withContentType=True) -> dict:
        """
        Returns the authorization headers
        """
        if withContentType:
            return {"Authorization": "Bearer " + self.getAccessToken(), "content-type": "application/json"}
        else:
           return {"Authorization": "Bearer " + self.getAccessToken()} 

    def getFramework(self) -> tuple:
        """
        Gets the framework from config file
        """
        config = self.getConfig()
        return (config['framework'])
    
    def getAllFilePathsForDirectory(self, dir: str):
        """
        Returns all file paths from given directory
        """
        paths = []
        for root, dirs, filenames in os.walk(dir, topdown=False):
            paths += ((os.path.join(root, name)) for name in filenames)
        return paths

    def getShasum(self, paths: list, directory: str) -> dict:
        """
        Calculates SHA1 sum for file
        """
        BUF_SIZE = 65536
        hashes = {}
        for path in paths:
            print("Hashing... " + path)
            sha1 = hashlib.sha1()
            with open(path, 'rb') as f:
                while True:
                    data = f.read(BUF_SIZE)
                    if not data: 
                        break
                    sha1.update(data)

                file_hash = sha1.hexdigest()
                print("Hashed path: " + file_hash)
                relative_path = path.replace(directory, '')
                hashes[relative_path[1:]] = file_hash
        
        return hashes
    
    def invertDict(self, dict: dict) -> dict:
        """
        Inverts a given dict
        """
        return {v: k for k, v in dict.items()}

    def createSite(self) -> tuple:
        """
        Creates a site

        Only for Netlify
        """
        json_headers = {"Authorization": "Bearer " + self.getAccessToken()} 
        r = requests.post(self.netlifyBaseUrl + '/sites', headers=json_headers)
        print("Site created with id: " + r.json()['id'])
        return r.json()
    
    def deploy(self, directory) -> tuple:
        """
        Creates a deployment by sending file hashes

        Only for Netlify
        """
        json_headers = self.getHeaders()
        paths = self.getAllFilePathsForDirectory(directory)
        # Get the shasum for all files in given directory
        fileHashes = self.getShasum(paths, directory)
        # Create a site on netlify
        site = self.createSite()
        data = {
            "files": fileHashes
        }
        deployUrl = self.netlifyBaseUrl + '/sites/' + site['id'] + '/deploys/'
        data_json = json.dumps(data)
        # Deploy the site to netlify
        r = requests.post(deployUrl, data=data_json, headers=json_headers)
        print("Deploying to Netlify...")
        return (r.json(), fileHashes, deployUrl)
    
    def getExistingDeployment(self, deploymentId, url):
        json_headers = self.getHeaders()
        getDeployUrl = url + deploymentId + '/'
        r = requests.get(url=getDeployUrl, headers=json_headers)
        if not r.ok:
            err('ERROR: Unable to fetch existing deployment')
            sys.exit(1)
            
        else:
            return r.json()
    
    def deployToNetlify(self, directory):
        accessToken = self.getAccessToken()
        deployment, fileHashes, deployUrl = self.deploy(directory)
        # Fetch the deployment id from deployment dict
        deployId = deployment['id']
        paths = self.getAllFilePathsForDirectory(directory)
        fileUploadHeaders = {"Authorization": "Bearer " + accessToken, 'content-type': "application/octet-stream"}
        for path in paths:
            print('Uploading ' + path.replace(directory, '') + "...")
            with open(path, 'rb') as file:
                r = requests.put(self.netlifyBaseUrl + '/deploys/' + deployId + '/files' + path.replace(directory, ''), file, headers=fileUploadHeaders)
                # Check if request was successful
                if r.ok:
                    print("File uploaded")
                if not r.ok:
                    err("ERROR: Unable to upload file")
                    print(r.content)
                    sys.exit(1)
                    
        
        # Check whether the application is deployed
        while deployment['state'] != 'ready':
            time.sleep
            # Get the deployment
            deployment = self.getExistingDeployment(deployId, deployUrl)
        
        print('\033[92m' + 'Successfully deployed at ' + deployment['deploy_ssl_url'] + '\033[0m')
    
    def uploadFileToVercel(self, directory):
        """
        Uploads files to the vercel API

        Only for Vercel
        """
        # Get all files in the directory
        paths = self.getAllFilePathsForDirectory(directory)
        # Get the shasum hashes for those files
        fileHashes = self.getShasum(paths, directory)
        for path in paths:
            print("Uploading " + path.replace(directory, '') + '...')
            with open(path, 'rb') as f:
                fileName = f.name.replace(directory, '')
                json_headers = {"Authorization": "Bearer " + self.getAccessToken(), "x-now-digest": fileHashes[fileName[1:]]}
                # Send file to vercel API for processing
                r = requests.post(self.vercelBaseUrl + '/v2/now/files', f.read(), headers=json_headers)
                if r.ok:
                    print("File uploaded")
                else:
                    err("ERROR: Unable to upload file")
                    sys.exit(1)
                    
    
    def deployToVercel(self, directory):
        self.uploadFileToVercel(directory)
        json_headers = self.getHeaders()
        paths = self.getAllFilePathsForDirectory(directory)
        files = []
        for path in paths:
            with open(path, 'r') as f:
                files.append({
                    "file": path.replace(directory, '')[1:],
                    "data": f.read()
                })

        data = {
            "name": self.projectName,
            "files": files,
            "projectSettings": {
                "framework": self.getFramework()
            }
        }
        r = requests.post(self.vercelBaseUrl + '/v12/now/deployments', json.dumps(data), headers=json_headers)

        if r.ok:
            print('\033[92m' + "Successfully deployed at " + r.json()['url'] + '\033[0m')    

    def awsCreateStaticSite(self) -> tuple:
        access_token, access_secret, region = self.getAWSConfig()
        s3 = boto3.resource('s3', 
        aws_access_key_id=access_token,
        aws_secret_access_key=access_secret)
        s3Client = boto3.client('s3', aws_access_key_id=access_token,
        aws_secret_access_key=access_secret)
        print("Creating bucket...")
        try:
            s3.create_bucket(
                Bucket=self.projectName,
                CreateBucketConfiguration={
                    'LocationConstraint': region
                }
            )
        except ClientError as err:
            err("ERROR: Bucket already exists!")
            

        s3Client.put_bucket_website(
            Bucket=self.projectName,
            WebsiteConfiguration={
            'ErrorDocument': {'Key': 'error.html'},
            'IndexDocument': {'Suffix': 'index.html'},
            }
        )
        print("Created bucket")

        bucket_policy = {
            'Version': '2012-10-17',
            'Statement': [{
                'Sid': 'Allow All',
                'Effect': 'Allow',
                'Principal': '*',
                "Action": [
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:PutObjectAcl"
                ],
                'Resource': "arn:aws:s3:::%s/*" % self.projectName
            }]
        }
        bucket_policy = json.dumps(bucket_policy)

        s3Client.put_bucket_policy(Bucket=self.projectName, Policy=bucket_policy)
        return (region)
    
    def deployToAWS(self, directory):
        region = self.awsCreateStaticSite()
        s3 = boto3.client('s3')
        s3.put_bucket_website(
            Bucket=self.projectName,
            WebsiteConfiguration={
            'ErrorDocument': {'Key': 'error.html'},
            'IndexDocument': {'Suffix': 'index.html'},
            }
        )
        
        if not os.path.exists(directory):
            err("ERROR: Target directory does not exist")
            err("ERROR: Deleting bucket")
            # Delete all objects in bucket
            boto3.resource('s3').Bucket(name=self.projectName).objects.all().delete()
            # Delete empty bucket
            s3.delete_bucket(Bucket=self.projectName)
            err("ERROR: Deleted bucket")
            sys.exit(1)
            

        paths = self.getAllFilePathsForDirectory(directory)

        for path in paths:
            s3.put_object(Body=open(path).read(),
                            Bucket=self.projectName,
                            Key=path.replace(directory, '')[1:],
                            ContentType='text/html')
        
        print('\033[92m' + f"Successfully deployed at  http://{self.projectName}.s3-website.{region}.amazonaws.com" + '\033[0m')

    def getSites(self) -> list:
        """
        Gets the sites and returns them

        Only for Netlify
        """
        json_headers = self.getHeaders()
        r = requests.get(self.netlifyBaseUrl + '/sites', headers=json_headers)
        return r.json()
    
    def getDeployments(self) -> dict:
        """
        Gets the deployments and returns the deployments as an array

        Only for Vercel
        """
        json_headers = self.getHeaders(False)
        r = requests.get(self.vercelBaseUrl + '/v5/now/deployments', headers=json_headers)
        return r.json()
