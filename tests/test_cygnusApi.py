from src.cygnet_adapter.adapter.api.cygnusApi import CygnusAPI
import unittest
from random import randint

class mockClusterState(object):
    def __init__(self):
        self.containers = dict()
    def addContainer(self, containerId):
        self.containers[containerId] = 1

    def stopContainer(self, containerId):
        self.containers[containerId] = 0
    def updateContainer(self, containerId, field, value):
        if field == 'State':
            self.containers[containerId] = value


class mockClient(object):
    def __init__(self):
        self.cluster_state = mockClusterState()


class CygnusApiTest(unittest.TestCase):

    def setUp(self):
        CygnusAPI.client = mockClient()
        self.api = CygnusAPI()
        self.containers = []
        self.dummy_req = dict()
        self.dummy_req['ClientRequest'] = dict()
        self.dummy_req['ClientRequest']['Request'] = None
        self.dummy_req['ServerResponse'] = 'dummy'

    def tearDown(self):
        del self.api

    def mock_createContainer(self, *args):
        randid = str(args[0])
        self.containers.append(randid)
        self.api.client.cluster_state.addContainer(randid)

    def mock_stopContainer(self, *args):
        self.api.client.cluster_state.stopContainer(str(args[0]))

    def mock_startContainer(self, *args):
        if type(args[0]) is dict:
            self.api.client.cluster_state.updateContainer(int(args[0]['ClientRequest']['Request'].split('/')[3]), 'State', 1)
            return
        self.api.client.cluster_state.updateContainer(args[0],'State',1)

    def test_getResponse(self):
        reqs = [
                '/version/containers/create',
                '/version/containers/alterme/stop',
                '/version/containers/alterme/start'
                ]
        self.api.createContainer    = self.mock_createContainer
        self.api.stopContainer      = self.mock_stopContainer
        self.api.startContainer     = self.mock_startContainer
        conts = ['1','2','3','4']

        ## Create
        for cont in conts:
            self.api.createContainer(cont)

        for cont in self.api.client.cluster_state.containers.itervalues():
            self.assertEquals(cont,1)

        for cont in conts:
            self.api.stopContainer(cont)
        for cont in self.api.client.cluster_state.containers.itervalues():
            self.assertEquals(cont, 0)

        for cont in conts:
            self.api.startContainer(cont)
        for cont in self.api.client.cluster_state.containers.itervalues():
            self.assertEquals(cont, 1)
        for cont in conts:
            self.dummy_req['ClientRequest']['Request'] = (reqs[randint(0,2)]).replace('alterme',cont)
            self.api.getResponse(self.dummy_req,'foo')

    def test_getEndpoint(self):
        req = '/'
        for i in range(0,randint(3,4)):
            for i in range(0,randint(1,10)):
                randnum = chr(randint(48,57))
                randlow = chr(randint(97,122))
                randup  = chr(randint(65,90))
                randarr = [randnum,randlow,randup]
                req = req + randarr[randint(0,2)]
            req = req + '/'
        ## erase the most right slash
        req     = req[:len(req)-1]
        ep      = self.api.getEndpoint(req)
        req     = req[1:]
        req_dis = req.split("/")
        if len(req_dis) == 4:
            self.assertIsInstance(ep, tuple)
            self.assertEquals(ep[0], req_dis[-1])
            self.assertEquals(ep[1], req_dis[-2])

        elif len(req_dis) == 3:
            self.assertIsInstance(ep, tuple)
            self.assertEquals(ep[0], req_dis[-1])
            self.assertEquals(ep[1],'')

if __name__ == "__main__":
    unittest.main()
