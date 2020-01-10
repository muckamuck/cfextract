import os
import sys
import logging
import json
import collections

from cfextract.utility import init_boto3_clients
from cfextract.utility import date_converter

logging.basicConfig(
        level=logging.INFO,
        format='[%(levelname)s] %(asctime)s (%(module)s) %(message)s',
        datefmt='%Y/%m/%d-%H:%M:%S'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
services = [
    'cloudformation'
]

verbose = False
clients = init_boto3_clients(services)
cf_client = clients.get('cloudformation')


class Worker:
    def __init__(self, stack_name, bucket, output_directory, cf_client):
        self.stack_name = stack_name
        self.bucket = bucket
        self.output_directory = output_directory
        self.cf_client = cf_client

    def work(self):
        try:
            response = self.cf_client.get_template(StackName=self.stack_name)
            logger.debug('response: %s', json.dumps(response, default=date_converter, indent=2))
            self.template_body = response.get('TemplateBody', None)
            if self.template_body is None:
                logger.error('stack_name=%s - not found', self.stack_name)
                return False

            response = self.cf_client.describe_stacks(StackName=self.stack_name)
            stack_count = len(response['Stacks'])
            if stack_count != 1:
                logger.error('stack_name=%s - describe_stacks found %s stacks', self.stack_name, stack_count)
                return False

            self.parameters = response['Stacks'][0].get('Parameters', [])
            logger.debug('parameters: %s', json.dumps(self.parameters, default=date_converter, indent=2))

            self.tags = response['Stacks'][0].get('Tags', [])
            logger.debug('tags: %s', json.dumps(self.tags, default=date_converter, indent=2))

            return self.write_stackility_stuff()
        except Exception as wtf:
            logger.error(wtf, exc_info=True)

        return False

    def write_stackility_stuff(self):
        try:
            if not os.path.isdir(self.output_directory):
                os.makedirs(self.output_directory)

            template_file_name = f'{self.output_directory}/{self.stack_name}.txt'
            ini_file_name = f'{self.output_directory}/{self.stack_name}.ini'
            with open(template_file_name, 'w') as f:
                if isinstance(self.template_body, collections.OrderedDict):
                    f.write(json.dumps(self.template_body, indent=2))
                else:
                    f.write(self.template_body)

            with open(ini_file_name, 'w') as f:
                f.write('[environment]\n')
                f.write(f'template={self.stack_name}.txt\n')
                f.write(f'stack_name={self.stack_name}\n')
                f.write(f'bucket={self.bucket}\n')
                f.write('region=us-east-1\n')
                f.write('\n')

                f.write('[tags]\n')
                for t in self.tags:
                    key = t.get('Key', None)
                    val = t.get('Value', None)
                    if key and val and key != 'CODE_VERSION_SD':
                        f.write(f'{key}={val}\n')

                f.write(f'tool=cf-extract\n')
                f.write('\n')

                if len(self.parameters) > 0:
                    f.write('[parameters]\n')
                    for p in self.parameters:
                        key = p.get('ParameterKey', None)
                        val = p.get('ParameterValue', None)
                        if key and val:
                            f.write(f'{key}={val}\n')
        except Exception as wtf:
            logger.error(wtf, exc_info=True)
