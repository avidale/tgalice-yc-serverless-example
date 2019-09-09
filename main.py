import logging
import tgalice


DEFAULT_MESSAGE = 'Hi! Please say "start" and I will tell you your future.'


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


dm = CheckableFormFiller('/function/code/form.yaml', default_message=DEFAULT_MESSAGE)
connector = tgalice.dialog_connector.DialogConnector(dialog_manager=dm)


def alice_handler(alice_request, context):
    return connector.respond(alice_request, source=tgalice.SOURCES.ALICE)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    server = tgalice.flask_server.FlaskServer(connector=connector)
    server.parse_args_and_run()
