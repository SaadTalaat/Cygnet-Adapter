from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
from twisted.internet.defer import inlineCallbacks

from cygnet_adapter.adapter.adapter import CygnusNetworkAdapter
from cygnet_adapter.adapter.api.cygnusApi import CygnusAPI
from clusterState import ClusterState


class RouterClient(ApplicationSession):

    def __init__(self, config):
        ApplicationSession.__init__(self,config)
        self.cluster_state = ClusterState(self)

    @inlineCallbacks
    def onJoin(self, details):

        print "Adapter Attached to Router"
        self.cluster_state.init(details)
        CygnusNetworkAdapter.client = self
        CygnusAPI.client = self
        yield self.subscribe(self.cluster_state)


    def leave(self, reason = None, log_message=None):
        self.cluster_state.leave()
        ApplicationSession.leave(self, reason, log_message)

    def disconnect(self):
        ApplicationSession.disconnect(self)


class HybridRunner(ApplicationRunner):

    def run(self, make, adapter, start_reactor=False):
        ApplicationRunner.run(self, make, start_reactor)
        self.adapter = adapter
