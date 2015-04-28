from __future__ import print_function
from os import environ

from twisted.internet import reactor

from cygnet_adapter.adapter.adapter import getAdapter
from cygnet_adapter.client.client import HybridRunner
from cygnet_adapter.client.client import RouterClient

if __name__ == '__main__':
    """
    We pull from the docker environment variable set during --link
    with this we can point to the correctly named sibling container.
    """
    # if environ['WAMP_WEBSOCKET_URL']:
    #     runner = HybridRunner(
    #         environ['WAMP_WEBSOCKET_URL'],
    #         environ['WAMP_REALM'])
    # elif:
    #     runner = HybridRunner(
    #         environ['WAMP_WEBSOCKET_URL'],
    #         environ['WAMP_REALM'])

    print(''.join(["ws://", environ['CROSSBAR_PORT_80_TCP_ADDR'], "/ws"]))
    print(environ['WAMP_REALM'])

    runner = HybridRunner(
        ''.join(["ws://", environ['CROSSBAR_PORT_80_TCP_ADDR'], "/ws"]),
        environ['WAMP_REALM'])
    adapter = getAdapter()
    reactor.listenTCP(80, adapter)
    runner.run(RouterClient, adapter)
    reactor.run()
