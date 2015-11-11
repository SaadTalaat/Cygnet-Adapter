from cygnet_common.Meta.Patterns import Singleton
import json


class CygnusAPI(object):
    __metaclass__ = Singleton
    client = None

    def __init__(self):
        pass

    def getEndpoint(self, requestString):
        # Resource Specific Requests
        # Request Pattern /version/resource/id/method
        # Generic Requests
        # Request Pattern /version/resource/method
        requestType = requestString.split('/')[1:]
        print("Request Type:", requestType)
        print("Request Length:", len(requestType))
        if len(requestType) == 4:
            return requestType[-1].split('?')[0], requestType[-2]
        else:
            return requestType[-1], ''

    # Handle Post Hooks #
    def getResponse(self, requestJson, nodes):
        method = requestJson['ClientRequest']['Method']
        if method == 'DELETE':
            return self.removeContainer(requestJson, nodes)
        endpoint = self.getEndpoint(requestJson['ClientRequest']['Request'])
        print("Response to hook", endpoint)
        return {'create': self.createContainer,
                'stop': self.stopContainer,
                'start': self.startContainer,
                'kill': self.noContent,
                'attach': self.attachContainer,
                'pause': self.noContent,
                'restart': self.noContent,
                'invalid': self.noContent,
                'json': self.jsonContainer
                }.get(endpoint[0], 'invalid')(requestJson, nodes)

    def createContainer(self, requestJson, nodes):
        # Store container id #
        config = {}
        config_tmp = json.loads(requestJson["ClientRequest"]["Body"])["Env"]

        for c in config_tmp:
            keyval = c.split("=")
            config[keyval[0]] = keyval[1]

        identification = json.loads(requestJson["ServerResponse"]["Body"])["Id"]
        # If we connected the client var should be passively set by the client [I should exit on failure]
        if self.client:
            self.client.cluster_state.addContainer(identification, config)
        else:
            print("[Error] Problem connecting to the router")
        nodes.append(identification)
        return {"PowerstripProtocolVersion": 1,
                "ModifiedServerResponse": requestJson["ServerResponse"]}

    def jsonContainer(self, requestJson, nodes):
        response_code = requestJson['ServerResponse']['Code']
        if (response_code & 400) == 400:
            return self.noContent(requestJson, nodes)
        response_body = json.loads(requestJson['ServerResponse']['Body'])
        identification = response_body['Id']
        state = response_body['State']
        name = response_body['Name']
        self.client.cluster_state.updateContainer(str(identification), "Name", str(name))
        if not state['Running']:
            self.client.cluster_state.stopContainer(identification)
        elif state['Running']:
            self.client.cluster_state.updateContainer(str(identification), "State", int(state['Running']))
        return {"PowerstripProtocolVersion": 1,
                "ModifiedServerResponse": requestJson["ServerResponse"]}

    def stopContainer(self, requestJson, nodes):
        endpoint = self.getEndpoint(requestJson['ClientRequest']['Request'])
        identification = endpoint[1]
        response_code = requestJson['ServerResponse']['Code']
        if (response_code & 400) == 400:
            return self.noContent(requestJson, nodes)
        print("Stopping Container:", identification)
        if self.client:
            self.client.cluster_state.stopContainer(identification)
        else:
            print("[Error] Problem connecting to the router")
        return self.noContent(requestJson, nodes)

    def startContainer(self, requestJson, nodes):
        endpoint = self.getEndpoint(requestJson['ClientRequest']['Request'])
        identification = endpoint[1]
        response_code = requestJson['ServerResponse']['Code']
        if (response_code & 400) == 400:
            return self.noContent(requestJson, nodes)
        print("Starting Contanier", identification)
        if self.client:
            print("Updating")
            self.client.cluster_state.updateContainer(str(identification), "State", 1)
        else:
            print("[Error] Problem connection to router")
        return self.noContent(requestJson, nodes)

    def removeContainer(self, requestJson, nodes):
        identification = requestJson['ClientRequest']['Request'].split("/")[-1]
        response_code = requestJson['ServerResponse']['Code']
        if (response_code & 400) == 400:
            return self.noContent(requestJson, nodes)
        if self.client:
            self.client.cluster_state.removeContainer(str(identification))
        else:
            print("[Error] Problem connecting to router")
        return self.noContent(requestJson, nodes)

    def noContent(self, requestJson, nodes):
        # Store Activity #
        return {"PowerstripProtocolVersion": 1,
                "ModifiedServerResponse": requestJson["ServerResponse"]}

    def attachContainer(self, requestJson, nodes):
        return {"PowerstripProtocolVersion": 1,
                "ModifiedServerResponse": requestJson["ServerResponse"]}
