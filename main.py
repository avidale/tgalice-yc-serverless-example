import boto3
import os
import random
import tgalice


DEFAULT_MESSAGE = 'Привет! Вы находитесь в навыке "Айтишный гороскоп". ' \
                  'Скажите "Старт", чтобы узнать, что сулят вам звёзды. ' \
                  'Скажите "Алиса, хватит", чтобы покинуть навык.'

FORECASTS = [
    'не выкатывате релизы в пятницу, и вас жду отличные выходные!',
    'возможно, пришло время избавиться от сотен непрочитанных сообщений. Чистый инбокс - к чистоте в карме!',
    'на этой неделе вам надо обязательно побывать в Парке Горького. '
    'Вероятно, вы встретите там человека, который изменит вашу жизнь.',
    'кажется, в вашей жизни близится время перемен. Может быть, это будет переход на Яндекс Облако?',
]


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


def make_dialog_manager(source_filename):
    dm = tgalice.dialog_manager.CascadeDialogManager(
        tgalice.dialog_manager.GreetAndHelpDialogManager(
            greeting_message=DEFAULT_MESSAGE,
            help_message=DEFAULT_MESSAGE,
            exit_message='До свидания, приходите в навык "Айтишный гороскоп" ещё!'
        ),
        CheckableFormFiller(source_filename, default_message=DEFAULT_MESSAGE)
    )
    return dm


if __name__ == '__main__':
    # local run or server-ful deploy
    # by default, store state in RAM
    connector = tgalice.dialog_connector.DialogConnector(dialog_manager=make_dialog_manager('form.yaml'))
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

    storage = tgalice.session_storage.S3BasedStorage(s3_client=s3, bucket_name='tgalice-test-cold-storage')

    dm = make_dialog_manager('/function/code/form.yaml')
    connector = tgalice.dialog_connector.DialogConnector(dialog_manager=dm, storage=storage)

    alice_handler = connector.serverless_alice_handler
