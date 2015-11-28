import etcd
from cygnet_common.generic.Container import Container


class EtcdClusterClient(etcd.Client):
    def __init__(self, host, nodeId, port=2379, protocol='http'):
        print(host)
        etcd.Client.__init__(self, host=host, port=port, protocol=protocol)
        print("INIT")
        self.nodeId = str(nodeId)
        print("NODE")

    # Custom methods

    def initStore(self):
        try:
            self.write("nodes", None, dir=True)
            return True
        except etcd.EtcdNotFile:
            try:
                self.read("nodes")
                return True
            except etcd.EtcdKeyNotFound:
                return False

    def addNode(self):
        node_key = "nodes/" + self.nodeId
        try:
            self.write(node_key, None, dir=True)
            self.write(node_key+"/state", 1, ttl=60)
            self.write(node_key+"/containers", None, dir=True)
            return []
        except etcd.EtcdNotFile:
            self.write(node_key+"/state", 1, ttl=60)
        # If we get here, node is not empty nor new
        containers = self.get(node_key+"/containers/")
        read_containers = []
        if containers:
            for container in containers.children:
                container = self.get(container.key)
                empty = {"Id": None,
                         "Name": None,
                         "Node": None,
                         "State": 0,
                         "Address": None}
                for leaf in container.children:
                    print(leaf)
                    empty[leaf.key.split("/")[-1]] = leaf.value
                container = Container(empty['Id'], self.nodeId)
                container.name = empty['Name']
                container.address = empty['Address']
                container.running(empty['State'])
                read_containers.append(container)
                print("")
        print("Read containers", read_containers)
        return read_containers

    def keepalive(self):
        print("Keep alive")
        node_key = "nodes/" + self.nodeId + "/state"
        try:
            node = self.get(node_key)
            node.ttl = 60
            self.update(node)
            return True
        except etcd.EtcdKeyNotFound:
            return False

    def _lockNode(self, nodePath):
        # traverse node path - check any parent nodes are locked.
        free = False
        for i in range(len(nodePath.split("/")), 0):
            try:
                lock = self.get("/".join(nodePath.split("/")[:i])+"/lock")
                if lock.value and lock.value != self.nodeId:
                    free &= False
                elif lock.value is None:
                    lock.value = self.nodeId
                    self.update(lock)
                    free &= True
                elif lock.value == self.nodeId:
                    free &= True
            except:
                if i == len(nodePath.split("/")):
                    self.write(nodePath+"/lock", self.nodeId, dir=False)
                else:
                    free &= True
                    continue
        return free

    def _unlockNode(self, nodePath):
        try:
            lock = self.get(nodePath+"/lock")
            lock.value = None
            self.update(lock)
        except:
            return

    def removeNode(self):
        node_key = "nodes/" + self.nodeId
        try:
            print("Removing Node")
            node = self.delete(node_key+"/state", recursive=True)
            return node
        except etcd.EtcdKeyNotFound:
            return None

    # A container shall be docker /json api response like ##
    def addContainer(self, container):
        container_key = "nodes/" + self.nodeId + "/containers/" + container.id

        try:
            self.write(container_key, None, dir=True)
            for key, value in container.items():
                current_key = container_key + "/" + key
                self.write(current_key, value, dir=False)
            return True
        except:
            return False

    def updateContainer(self, container, key=None):
        container_key = "nodes/" + self.nodeId + "/containers/" + container.id
        if key:
            current_key = container_key + "/" + key
        try:
            if key:
                node = self.get(current_key)
                node.value = container[key]
                self.update(node)
                return True
            else:
                for key2, value in container.items():
                    current_key = container_key+"/"+key2
                    node = self.get(current_key)
                    node.value = container[key2]
                    self.update(node)
                return True
        except:
            return False

    def removeContainer(self, container):
        container_key = "nodes/" + self.nodeId + "/containers/" + container.id
        print("Removing container", container_key)
        try:
            self.delete(container_key, recursive=True)
            return True
        except:
            return False
