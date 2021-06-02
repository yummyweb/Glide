from src.api import Api
import requests

class Deployment:
    def __init__(self, deploymentName, cloudName):
        self.deploymentName = deploymentName
        self.cloudName = cloudName
    
    def deployToNetlify(self):
        api = Api(self.deploymentName)
        if self.cloudName == "netlify":
            accessToken = api.getAccessToken()
            print(accessToken)

deployment =Deployment('hi', 'netlify')