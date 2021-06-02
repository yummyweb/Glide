from src.api import Api

class Deployment:
    def __init__(self, deploymentName, directoryToDeploy):
        self.deploymentName = deploymentName
        self.directoryToDeploy = directoryToDeploy
    
    def deployToNetlify(self):
        api = Api(self.deploymentName)
        api.uploadFile(self.directoryToDeploy)