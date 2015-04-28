# from __future__ import print_function
# from os import environ

# from twisted.internet import reactor

# from adapter.adapter import getAdapter
# from client.client import HybridRunner
# from client.client import RouterClient

__version__ = "0.1.0"

# MOVED TO __main__.py

# if __name__ == '__main__':
#     """
#     We pull from the docker environment variable set during --link
#     with this we can point to the correctly named sibling container.
#     """
#     # if environ['WAMP_WEBSOCKET_URL']:
#     #     runner = HybridRunner(
#     #         environ['WAMP_WEBSOCKET_URL'],
#     #         environ['WAMP_REALM'])
#     # elif:
#     #     runner = HybridRunner(
#     #         environ['WAMP_WEBSOCKET_URL'],
#     #         environ['WAMP_REALM'])

#     print(''.join(["ws://", environ['CROSSBAR_PORT_80_TCP_ADDR'], "/ws"]))
#     print(environ['WAMP_REALM'])

#     runner = HybridRunner(
#         ''.join(["ws://", environ['CROSSBAR_PORT_80_TCP_ADDR'], "/ws"]),
#         environ['WAMP_REALM'])
#     adapter = getAdapter()
#     reactor.listenTCP(80, adapter)
#     runner.run(RouterClient, adapter)
#     reactor.run()
