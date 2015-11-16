from twisted.web import resource, server
import json
from pprint import pprint
from cygnet_adapter.adapter.api.cygnusApi import CygnusAPI


class CygnusNetworkAdapter(resource.Resource):
    isLeaf = True
    client = None

    def __init__(self):
        resource.Resource.__init__(self)
        # Each nodes is identified by its peer address
        # Example:
        # { '172.17.0.31' : ['containeridentifier1', 'containeridentifier2'] }
        self.nodes = []
        self.api = CygnusAPI()

    def render_POST(self, request):
        print(request.method, "In post")
        print('')
        requestJson = json.loads(request.content.read())
        pprint(requestJson)
        if requestJson["Type"] == 'pre-hook':
            return self.customHandlePre(request, requestJson)
        elif requestJson["Type"] == 'post-hook':
            return self.customHandlePost(request, requestJson)

    def customHandlePre(self, request, request_json):
        response = {
            "PowerstripProtocolVersion": 1,
            "ModifiedClientRequest": request_json["ClientRequest"],
        }
        # TODO: Capture the environment variables we use.
        pprint(request_json)
        request.write(json.dumps(response))
        request.finish()
        return server.NOT_DONE_YET

    def customHandlePost(self, request, requestJson):
        # We need to store a container identifier and its peer address
        # print requestJson
        # self.nodes.append(
        #     json.loads(requestJson["ServerResponse"]["Body"])["Id"])
        # print "Node registered"
        # response = {
        #        "PowerstripProtocolVersion": 1,
        #        "ModifiedServerResponse": requestJson["ServerResponse"]}
        response = self.api.getResponse(requestJson, self.nodes)
        request.write(json.dumps(response))
        request.finish()
        return server.NOT_DONE_YET


def getAdapter():
    root = resource.Resource()
    root.putChild("cygnus-adapter", CygnusNetworkAdapter())
    return server.Site(root)
