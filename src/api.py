import hashlib
import requests
import os
import json
import time
import vercel
from src.exceptions import ConfigFileException

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
            raise ConfigFileException("File not found.")

        return eval(f.read())

    def getClientIdAndClientSecret(self) -> tuple:
        """
        Gets the config file and returns the client id and secret
        """
        config = self.getConfig()
        return (config['client_id'], config['client_secret'])
    
    def getAccessToken(self) -> tuple:
        """
        Gets the config file and returns the access token
        """
        config = self.getConfig()
        return (config['access_token'])
    
    def getHeaders(self, withContentType=True) -> dict:
        """
        Returns the authorization headers
        """
        if withContentType:
            return {"Authorization": "Bearer " + self.getAccessToken(), "content-type": "application/json"}
        else:
           return {"Authorization": "Bearer " + self.getAccessToken()} 
    
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
    
    def getDeployments(self) -> list:
        """
        Gets the deployments and returns the deployments as an array
        """
        json_headers = self.getHeaders(False)
        r = requests.get(self.vercelBaseUrl + '/v5/now/deployments', headers=json_headers)
        return r.json()
    
    def deploy(self, directory) -> tuple:
        """
        Creates a deployment by sending file hashes

        Only for Netlify
        """
        json_headers = self.getHeaders()
        paths = self.getAllFilePathsForDirectory(directory)
        fileHashes = self.getShasum(paths, directory)
        site = self.createSite()
        data = {
            "files": fileHashes
        }
        deployUrl = self.netlifyBaseUrl + '/sites/' + site['id'] + '/deploys/'
        data_json = json.dumps(data)
        r = requests.post(deployUrl, data=data_json, headers=json_headers)
        print("Deploying to Netlify...")
        return (r.json(), fileHashes, deployUrl)
    
    def getExistingDeployment(self, deploymentId, url):
        json_headers = self.getHeaders()
        getDeployUrl = url + deploymentId + '/'
        r = requests.get(url=getDeployUrl, headers=json_headers)
        if not r.ok:
            print('ERROR: Unable to fetch existing deployment')
            print(r.content)
        else:
            return r.json()
    
    def uploadFile(self, directory):
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
                    print('\033[91m' + "ERROR:" + '\033[0m' + " Unable to upload file")
                    print(r.content)
            
        while deployment['state'] != 'ready':
            time.sleep(1)
            deployment = self.getExistingDeployment(deployId, deployUrl)
        
        print('\033[92m' + 'Successfully deployed at ' + deployment['deploy_ssl_url'] + '\033[0m')
    
    def getSites(self) -> list:
        json_headers = self.getHeaders()
        r = requests.get(self.netlifyBaseUrl + '/sites', headers=json_headers)
        return r.json()