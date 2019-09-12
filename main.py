import logging
import os
import random
import tgalice

import boto3
import codecs
import json
from tgalice.storage.session_storage import BaseStorage
from botocore.exceptions import ClientError


DEFAULT_MESSAGE = 'Привет! Вы в приватном навыке "Айтишный гороскоп". ' \
                  'Скажите "Старт", чтобы узнать, что сулят вам звёзды. ' \
                  'Скажите "Алиса, хватит", чтобы покинуть навык.'

FORECASTS = [
    'не выкатывате релизы в пятницу, и вас жду отличные выходные!',
    'возможно, пришло время избавиться от сотен непрочитанных сообщений. Чистый инбокс - к чистоте в карме!',
    'на этой неделе вам надо обязательно побывать в Парке Горького. '
    'Вероятно, вы встретите там человека, который изменит вашу жизнь.',
    'кажется, в вашей жизни близится время перемен. Может быть, это будет переход на Яндекс.Облако?',
]


class S3BasedStorage(BaseStorage):
    def __init__(self, s3_client, bucket_name, prefix=''):
        super(BaseStorage, self).__init__()
        self.s3_client = s3_client
        self.bucket_name = bucket_name
        self.prefix = prefix

    def modify_key(self, key):
        return self.prefix + key

    def get(self, key):
        try:
            result = self.s3_client.get_object(Bucket=self.bucket_name, Key=self.modify_key(key))
            body = result['Body']
            reader = codecs.getreader("utf-8")
            return json.load(reader(body))
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                return {}
            else:
                raise e

    def set(self, key, value):
        self.s3_client.put_object(Bucket=self.bucket_name, Key=self.modify_key(key), Body=json.dumps(value))


class CheckableFormFiller(tgalice.dialog_manager.form_filling.FormFillingDialogManager):
    SIGNS = {
        'январь': 'Козерог',
        'февраль': 'Водолей',
        'март': 'Рыбы',
        'апрель': 'Овен',
        'май': 'Телец',
        'июнь': 'Близнецы',
        'июль': 'Рак',
        'август': 'Лев',
        'сентябрь': 'Дева',
        'октябрь': 'Весы',
        'ноябрь': 'Скорпион',
        'декабрь': 'Стрелец',
    }

    def handle_completed_form(self, form, user_object, ctx):
        response = tgalice.dialog_manager.base.Response(
            text='Спасибо, {}! Теперь мы знаем: вам {} лет, и вы {}. \n'
                 'Вот это вам, конечно, повезло! Звёзды говорят вам: {}'.format(
                form['fields']['name'],
                2019 - int(form['fields']['year']),
                self.SIGNS[form['fields']['month']],
                random.choice(FORECASTS),
            ),
            user_object=user_object,
        )
        return response


if __name__ == '__main__':
    # local run or server-ful deploy
    logging.basicConfig(level=logging.INFO)

    dm = CheckableFormFiller('form.yaml', default_message=DEFAULT_MESSAGE)
    connector = tgalice.dialog_connector.DialogConnector(dialog_manager=dm)  # by default, store state in RAM
    server = tgalice.flask_server.FlaskServer(connector=connector)
    server.parse_args_and_run()
else:
    # serverless deploy
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

