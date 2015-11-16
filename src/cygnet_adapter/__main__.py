import sys
import click
from twisted.internet import reactor
from cygnet_adapter.client.clusterState import ClusterState
from cygnet_adapter.adapter.adapter import getAdapter
from cygnet_adapter.client.client import HybridRunner
from cygnet_adapter.client.client import RouterClient

# Why does this file exist, and why __main__?
# For more info, read:
# - https://www.python.org/dev/peps/pep-0338/
# - https://docs.python.org/2/using/cmdline.html#cmdoption-m
# - https://docs.python.org/3/using/cmdline.html#cmdoption-m
usage = '''[Usage]
--router-addr       : the wamp router address (e.g. '0.0.0.0')
--etcd-server-addr  : address of etcd node to read cluster state from (e.g. '0.0.0.0:7001')
--router-realm      : crossbar router realm to join (e.g. 'cygnet')
'''


# If address is not formatted correctly or illegal port is provided
# etcdClient will complain so no need to worry about it
def validate_router_addr(ctx, param, value):
    if not value:
        print(usage)
        raise click.MissingParameter('--router-addr is missing')
    return value


def validate_etcd_addr(ctx, param, value):
    if len(value.split(':')) != 2:
        print(usage)
        raise click.BadParameter('--etcd-server-addr is formatted incorrectly')
        try:
            int(value.split(':')[1])
        except:
            print(usage)
            raise click.BadParameter('--etcd-addr has illegal port number provided')
    return value


@click.command()
@click.option('--router-addr', envvar='CYGNET_CROSSBAR_ADDR', callback=validate_router_addr)
@click.option('--router-realm', envvar='CYGNET_CROSSBAR_REALM', default='cygnet')
@click.option('--etcd-server-addr', envvar='CYGNET_ETCD_ADDR', default='0.0.0.0:7001', callback=validate_etcd_addr)
def main(router_addr, router_realm, etcd_server_addr):
    # click.echo(repr(names))
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
    try:
        router_addr = router_addr.decode('utf-8')
        router_realm = router_realm.decode('utf-8')
    except:
        pass
    ClusterState.etcd_addr = (etcd_server_addr.split(':')[0], etcd_server_addr.split(':')[1])
    runner = HybridRunner(
        ''.join(["ws://", router_addr, "/ws"]),
        router_realm)
    adapter = getAdapter()
    reactor.listenTCP(80, adapter)
    runner.run(RouterClient, adapter)
    reactor.run()


if __name__ == "__main__":
    sys.exit(main())
