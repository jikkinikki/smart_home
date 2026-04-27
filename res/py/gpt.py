import openai
import json
import secrets

class Gpt:
    def __init__(self):
        self.model_name = "gpt-4o-mini"
        self.api_key = secrets.gpt_api_key
        self.client = openai.OpenAI(api_key=self.api_key, )

    def prepare_commands(self, commands):

        i = 0
        command_str = ""
        for command in commands:

            # new_commands.append({
            #     "desc": command["desc"],
            #     "index": i
            # })
            command_str += f"{i}{command['desc']}\n"

            i += 1

        return command_str

    def complete(self, prompt, commands):

        # https://platform.openai.com/tokenizer

        commands = self.prepare_commands(commands)

        system_content = "You are the sassy smart home 'Bixby' that figures out what user wants to do. " + commands

        # print(prompt)
        # print(system_content)

        response = self.client.chat.completions.create(
            model = self.model_name,
            messages = [
                {
                    "role": "system", 
                    "content": system_content
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            response_format = {
                "type": "json_schema",
                "json_schema": {
                    "name": "response_schema",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "command_id": {
                                "description": "Command id, -1 if nothing matches",
                                "type": "number"
                            },
                            "explanation": {
                                "description": "Very short related joke in the \"common tounge\" ONLY if command_id is -1",
                                "type": "string"
                            },
                            "parameters":{
                                "description": "Parameters for the command IF required",
                                "type": "array",
                                "items": {}
                            }
                        },
                        "required": ["command_id"],
                        "additionalProperties": False
                    }
                }
            }
        )

        print(response.choices[0].message.content)
        return json.loads(response.choices[0].message.content)

# -TEST CODE------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    commands = [

        {
            "desc": "turn off",
            "btn": "off",
        },
        {
            "desc": "turn on",
            "btn": "on",
        },
        {
            "desc": "party",
        },
        {
            "desc": "set brightness",
        },
        {
            "desc": "set Kelvin",
        },
        {
            "desc": "toggle ambient",
        },
        {
            "desc": "toggle lights, clap clap",
        }
    ]

    gpt = Gpt()
    # gpt.complete("Turn on the lights", commands)
    gpt.complete("hey Bixby. clap clap", commands)