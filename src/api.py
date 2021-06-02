import ast
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

        return ast.literal_eval(f.read())

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
        return {"Authorization": "Bearer " + self.getAccessToken()}
    
    def getAllFilePathsForDirectory(self, dir):
        paths = []
        for root, dirs, filenames in os.walk(dir, topdown=False):
            paths += ((os.path.join(root, name)) for name in filenames)
        return paths

    def getShasum(self, paths, directory) -> dict:
        BUF_SIZE = 65536
        hashes = {}
        for path in paths:
            sha1 = hashlib.sha1()
            with open(path, 'rb') as f:
                while True:
                    data = f.read(BUF_SIZE)
                    if not data: 
                        break
                    sha1.update(data)

                file_hash = sha1.hexdigest()
                relative_path = path.replace(directory, '')
                hashes[relative_path] = file_hash
        
        return hashes

    def createSite(self) -> dict:
        json_headers = self.getHeaders()
        r = requests.post(self.netlifyBaseUrl + '/sites', headers=json_headers)
        return r.json()
    
    def deploy(self, directory):
        json_headers = self.getHeaders()
        paths = self.getAllFilePathsForDirectory(directory)
        fileHashes = self.getShasum(paths, directory)
        site = self.createSite()
        data = json.dumps({
            "files": fileHashes,
            "draft": True
        })
        r = requests.post(self.netlifyBaseUrl + '/sites/' + site['id'] + '/deploys', data, headers=json_headers)
        return r.json()