"""
The command line interface to stackility.

Major help from: https://www.youtube.com/watch?v=kNke39OZ2k0
"""
import boto3
import logging
import click
import sys
import platform

from cfextract.utility import init_boto3_clients
from cfextract.worker import Worker

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s (%(module)s) %(message)s',
    datefmt='%Y/%m/%d-%H:%M:%S'
)

logger = logging.getLogger(__name__)

services = [
    'cloudformation'
]

valid_systems = [
    'linux',
    'darwin'
]


@click.group()
@click.version_option(version='0.1.0')
def cli():
    pass


@cli.command()
@click.option('--stack', '-s', help='the stack to dump', required=True)
@click.option('--bucket', '-b', help='the bucket to use for the artifacts', required=True)
@click.option('--output', '-o', help='the output directory', required=True)
@click.option('--profile', '-p', help='profile for the STS client creation')
@click.option('--region', help='AWS region')
def extract(stack, bucket, output, profile, region):
    try:
        clients = init_boto3_clients(services, profile=profile, region=region)
        cf_client = clients.get('cloudformation', None)
        worker = Worker(stack, bucket, output, cf_client)
        worker.work()
    except Exception as wtf:
        print('echo assume() exploded: {}'.format(wtf))
        sys.exit(1)


def find_myself():
    s = boto3.session.Session()
    region = s.region_name
    if region:
        return region
    else:
        return 'us-east-1'


def verify_real_system():
    try:
        current_system = platform.system().lower()
        return current_system in valid_systems
    except:
        return False

if not verify_real_system():
    print('error: unsupported system')
    sys.exit(1)
