from autobahn import wamp
from cygnet_common.design import Task
from cygnet_common import strtypes
from copy import deepcopy
from cygnet_adapter.client.etcdCluster import EtcdClusterClient
import uuid


class ClusterState(object):
    etcd_addr = None

    def __init__(self, session):
        self.session = session
        self.health = {}
        self.etcd_client = None

    def init(self, details):
        self.containers = []
        try:
            f = open("/cygnus/node", 'r')
            node_id = f.read()
            f.close()
        except IOError:
            node_id = str(uuid.uuid1())
            f = open("/cygnus/node", 'w')
            f.write(node_id)
            f.close()
        self.node = {'id': node_id, 'session': details.session, 'containers': self.containers}
        self.etcd_client = EtcdClusterClient(self.etcd_addr[0], self.node['id'], int(self.etcd_addr[1]))
        self.etcd_client.initStore()
        print("Initiated")
        self.nodes = [self.node]
        prev_containers = self.etcd_client.addNode()
        if prev_containers:
            for container in prev_containers:
                self.node['containers'].append(container)

        self.session.publish("nodes.sync_request", self.node)
        self.health_check = Task.TaskInterval(10, self.keepalive)
        self.health_check.start()

    def leave(self):
        self.nodes.remove(self.node)
        self.etcd_client.removeNode()
        self.session.publish("nodes.sync_nodes", self.nodes)

    def keepalive(self):
        self.etcd_client.keepalive()
        if not self.health:
            return
        self.session.publish("nodes.sync_request", self.node)
        most = max([health for health in self.health.values()])
        health_tmp = deepcopy(self.health)
        for nodeId, health in health_tmp.items():
            # find node dictionary
            mask = [node['session'] == nodeId for node in self.nodes]
            # If there has not been a keepalive in 5 health-checks
            # remove node
            if (most - health) > 5 and sum(mask):
                print("Remove", nodeId, self.node)
                node_idx = mask.index(True)
                self.nodes.pop(node_idx)
                self.health.pop(nodeId)
                self.session.publish("nodes.sync_nodes", self.nodes)

    def addContainer(self, containerId, config):
        if "CYGNET_INTERNAL_IP" in config and "CYGNET_INTERNAL_SUBNET" in config:
            addr = "/".join([config["CYGNET_INTERNAL_IP"], config["CYGNET_INTERNAL_SUBNET"]])
        else:
            addr = None
            return False
        exists = filter(lambda x: str(x) == addr, [container["Address"] for container in self.node['containers']])
        if addr and exists:
            return False
        container = {"Id": containerId, "Name": None, "Node": self.node['id'], "State": 1, "Address": addr}
        self.nodes.remove(self.node)
        self.node['containers'].append(container)
        self.nodes.append(self.node)
        self.session.publish("ovs.hook_container", container)
        self.session.publish("nodes.sync_nodes", self.nodes)
        self.etcd_client.addContainer(container)
        print("Container added", self.nodes)
        return True

    def stopContainer(self, containerId):
        if not containerId or type(containerId) not in [str, bytes]:
            print("Bad Identification")
            return
        else:
            cont_with_id = filter(lambda x: str(x['Id']).find(containerId) == 0, self.node['containers'])
            cont_with_name = filter(lambda x: str(x['Name']).find(containerId) == 1, self.node['containers'])
            matched = cont_with_id or cont_with_name
        if len(matched) == 0 or len(matched) > 1:
            print("Two or more node match identification criteria")
            return
        container = matched[0]
        if not container:
            return
        elif container["State"] == 0:
            return
        container["State"] = 0
        self.session.publish("ovs.unhook_container", container)
        self.session.publish("nodes.sync_nodes", self.nodes)
        self.etcd_client.updateContainer(container, "State")

    def removeContainer(self, containerId):
        if not containerId or type(containerId) not in [str, bytes]:
            print("Bad Identification")
            return
        else:
            cont_with_id = filter(lambda x: str(x['Id']).find(containerId) == 0, self.node['containers'])
            cont_with_name = filter(lambda x: str(x['Name']).find(containerId) == 1, self.node['containers'])
            matched = cont_with_id or cont_with_name
        if len(matched) == 0 or len(matched) > 1:
            print("Two or more node match identification criteria")
            return
        container = matched[0]
        if not container:
            return
        self.node['containers'].remove(container)
        self.session.publish("ovs.unhook_container", container)
        self.session.publish("nodes.sync_nodes", self.nodes)
        self.etcd_client.removeContainer(container)

    def updateContainer(self, identification, field, value):
        if not identification or type(identification) != str:
            print("Bad identification")
            return
        else:
            # Identification or a name?
            cont_with_id = filter(lambda x: str(x['Id']).find(identification) == 0, self.node['containers'])
            cont_with_name = filter(lambda x: str(x['Name']).find(identification) == 1, self.node['containers'])
            matched = (cont_with_id or cont_with_name)
        if not matched or len(matched) > 1:
            return
        container = matched[0]
        print("updating container", identification, field, value)
        if field.find("State") == 0 and len(field) == len("State"):
            if container[field] == 0 and value == 1:
                self.session.publish("ovs.hook_container", container)
            elif container[field] == 1 and value == 0:
                self.session.publish("ovs.unhook_container", container)
            else:
                return
        container[field] = value
        self.etcd_client.updateContainer(container, field)

    @wamp.subscribe(u'nodes.sync_nodes')
    def syncNodes(self, nodes):

        # Are we syncing on a startup?
        if len(self.nodes) <= len(nodes) and len(self.nodes) == 1:
            for node in nodes:
                if node not in self.nodes:
                    self.nodes.append(node)
                    if self.health and node['id'] not in self.health:
                        self.health[node['id']] = max([v for v in self.health.values()])
            print("Synced Nodes:", self.nodes)
        # Are we broadcasting a leave?
        if len(nodes) < len(self.nodes):
            for node in self.nodes:
                if node not in nodes:
                    self.nodes.remove(node)
            print("After a leave", self.nodes)

    @wamp.subscribe(u'nodes.sync_request')
    def syncRequest(self, origin):
        if origin['id'] not in self.health:
            self.health[origin['id']] = 0
        self.health[origin['id']] += 1
        self.health[origin['id']] = max([v for v in self.health.values()])
        if origin not in self.nodes:
            self.nodes.append(origin)
        self.session.publish("nodes.sync_nodes", self.nodes)
