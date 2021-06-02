import hashlib
import requests
import os
import json
from src.exceptions import ConfigFileException

class Api:
    def __init__(self, projectName):
        self.projectName = projectName
        self.netlifyBaseUrl = 'https://api.netlify.com/api/v1'

    def getConfig(self) -> dict:
        """
        Reads the config file and returns the file contents as dict
        """
        try:
            f = open(self.projectName + ".glide", "r")
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
        config = self.getConfig()
        return (config['access_token'])
    
    def getHeaders(self) -> dict:
        """
        Returns the authorization headers
        """
        return {"Authorization": "Bearer " + self.getAccessToken(), "content-type": "application/json"}
    
    def getAllFilePathsForDirectory(self, dir):
        paths = []
        for root, dirs, filenames in os.walk(dir, topdown=False):
            paths += ((os.path.join(root, name)) for name in filenames)
        return paths

    def getShasum(self, paths, directory) -> dict:
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

    def createSite(self) -> dict:
        json_headers = {"Authorization": "Bearer " + self.getAccessToken()} 
        r = requests.post(self.netlifyBaseUrl + '/sites', headers=json_headers)
        print("Site created with id: " + r.json()['id'])
        return r.json()
    
    def deploy(self, directory) -> tuple:
        json_headers = self.getHeaders()
        paths = self.getAllFilePathsForDirectory(directory)
        fileHashes = self.getShasum(paths, directory)
        site = self.createSite()
        data = {
            "files": fileHashes
        }
        data_json = json.dumps(data)
        r = requests.post(self.netlifyBaseUrl + '/sites/' + site['id'] + '/deploys', data=data_json, headers=json_headers)
        print("Deploying to Netlify...")
        return (r.json(), fileHashes)
    
    def uploadFile(self, directory):
        accessToken = self.getAccessToken()
        deployment, fileHashes = self.deploy(directory)
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
    
    def getSites(self) -> list:
        json_headers = self.getHeaders()
        r = requests.get(self.netlifyBaseUrl + '/sites', headers=json_headers)
        return r.json()