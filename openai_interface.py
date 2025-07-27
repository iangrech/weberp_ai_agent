import configparser
import openai
import json


class ai:
    system_message = []
    user_message = []
    assistant_message = []

    def __init__(self, config_file: str = 'config.cfg'):
        config = configparser.ConfigParser()
        config.read(config_file)

        if not config.has_section('openai'):
            raise ValueError("Configuration file must have a [openai] section")

        self.api_key = config['openai']['api_key']
        self.model = config['openai']['model']
        self.temperature = float(config['openai']['temperature'])
        self.max_tokens  = int(config['openai']['max_tokens'])


    def ask(self):
        openai.api_key = self.api_key

        response = openai.chat.completions.create(
                                                    model=self.model,
                                                    messages=[
                                                                {
                                                                    'role': 'system',
                                                                    'content': ' '.join(self.system_message) ,
                                                                },
                                                                {
                                                                    'role': 'user',
                                                                    'content': ' '.join(self.user_message),
                                                                },
                                                                {
                                                                    'role': 'assistant',
                                                                    'content': ' '.join(self.assistant_message),
                                                                }
                                                            ],
                                                    max_completion_tokens = self.max_tokens,
                                                    temperature = self.temperature
                                                    )

        return response.choices[0].message.content

    def reset_messages(self, include_assistant=False):
        self.system_message = []
        self.user_message = []
        if include_assistant:
            self.assistant_message = []