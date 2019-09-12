import logging
import os
import tgalice

import boto3
import codecs
import json
from tgalice.storage.session_storage import BaseStorage
from botocore.exceptions import ClientError


DEFAULT_MESSAGE = 'Hi! Please say "start" and I will tell you your future. k1={}'.format(os.environ['k1'])


class S3BasedStorage(BaseStorage):
    def __init__(self, s3_client, bucket_name):
        super(BaseStorage, self).__init__()
        self.s3_client = s3_client
        self.bucket_name = bucket_name

    def get(self, key):
        try:
            result = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            body = result['Body']
            reader = codecs.getreader("utf-8")
            return json.load(reader(body))
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                return {}
            else:
                raise e

    def set(self, key, value):
        self.s3_client.put_object(Bucket=self.bucket_name, Key=key, Body=json.dumps(value))


class CheckableFormFiller(tgalice.dialog_manager.form_filling.FormFillingDialogManager):
    SIGNS = {
        'jan': 'The Goat',
        'feb': 'The Water Bearer',
        'mar': 'The Fishes',
        'apr': 'The Ram',
        'may': 'The Bull',
        'jun': 'The Twins',
        'jul': 'The Crab',
        'aug': 'The Lion',
        'sep': 'The Virgin',
        'oct': 'The Balance',
        'nov': 'The Scorpion',
        'dec': 'The Archer',
    }

    def handle_completed_form(self, form, user_object, ctx):
        response = tgalice.dialog_manager.base.Response(
            text='Thank you, {}! Now we know: you are {} years old and you are probably {}. Lucky you!'.format(
                form['fields']['name'],
                2019 - int(form['fields']['year']),
                self.SIGNS[form['fields']['month']]
            ),
            user_object=user_object,
        )
        return response


session = boto3.session.Session()
s3 = session.client(
    service_name='s3',
    endpoint_url='https://storage.yandexcloud.net',
    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
    region_name='ru-central1',
)

storage = S3BasedStorage(s3_client=s3, bucket_name='tgalice-test-state-storage')


dm = CheckableFormFiller('/function/code/form.yaml', default_message=DEFAULT_MESSAGE)
connector = tgalice.dialog_connector.DialogConnector(dialog_manager=dm, storage=storage)


def alice_handler(alice_request, context):
    return connector.respond(alice_request, source=tgalice.SOURCES.ALICE)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    server = tgalice.flask_server.FlaskServer(connector=connector)
    server.parse_args_and_run()
