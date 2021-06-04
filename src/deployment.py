from src.api import Api

class Deployment:
    def __init__(self, deploymentName, directoryToDeploy):
        self.deploymentName = deploymentName
        self.directoryToDeploy = directoryToDeploy
        self.api = Api(self.deploymentName)
    
    def deployToNetlify(self):
        self.api.deployToNetlify(self.directoryToDeploy)
    
    def deployToVercel(self):
        self.api.deployToVercel(self.directoryToDeploy)
    
    def deployToAWS(self):
        self.api.deployToAWS(self.directoryToDeploy)
