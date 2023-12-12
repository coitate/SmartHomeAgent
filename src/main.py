import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from switchbot_client.client import SwitchBotClient

load_dotenv()

SWITCHBOT_TOKEN = os.getenv("SWITCHBOT_TOKEN")
SWITCHBOT_SECRET_KEY = os.getenv("SWITCHBOT_SECRET_KEY")
ORGANIZATION_ID = os.getenv("ORGANIZATION_ID")
API_KEY = os.getenv("API_KEY")


def main():
    sb_client = SwitchBotClient(token=SWITCHBOT_TOKEN, secret_key=SWITCHBOT_SECRET_KEY)
    ai_client = OpenAI(organization=ORGANIZATION_ID, api_key=API_KEY)
    model = "gpt-3.5-turbo-1106"
    available_functions = {
        f"{sb_client.control_device_with_name.__name__}": sb_client.control_device_with_name
    }
    with open("func_definitions/control_device_with_name.json") as f:
        tools = [json.load(f)]

    messages = [
        {
            "role": "system",
            "content": "You are a smart home agent that can control devices in the home.",
        },
        {"role": "system", "content": "Any device names must be provided in Japanese."},
        {
            "role": "system",
            "content": "When controlling curtains, turnOn means open and turnOff means close.",
        },
    ]

    while True:
        prompt = input("Q: ")
        if prompt == "q" or prompt == "":
            break

        messages.append({"role": "user", "content": prompt})

        response = ai_client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=1000,
            tools=tools,
            tool_choice="auto",
        )

        choice = response.choices[0]
        finish_reason = choice.finish_reason

        if finish_reason == "stop":
            answer = choice.message.content
            messages.append({"role": "assistant", "content": answer})
        elif finish_reason == "tool_calls":
            message = choice.message
            messages.append(message)
            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                if not function_name in available_functions:
                    print(function_name, "is not available")
                    continue

                function_to_call = available_functions[function_name]
                function_args = json.loads(tool_call.function.arguments)
                values = list(function_args.values())
                function_output = function_to_call(*values)
                print(function_name, function_args, "function_output:", function_output)

                content = function_args
                content["function_output"] = function_output
                message = {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": str(content),
                }
                messages.append(message)

            response = ai_client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=1000,
                tools=tools,
                tool_choice="auto",
            )

            answer = response.choices[0].message.content
            messages.append({"role": "assistant", "content": answer})

        print("A:", answer)

    print("----- Chat history -----")
    for msg in messages:
        msg_dict = dict(msg)
        if msg_dict["content"] is None:
            continue

        if msg_dict["role"] == "assistant":
            indent = "\t>>"
        else:
            indent = "\t\t>>"
        print(msg_dict["role"], indent, msg_dict["content"])


if __name__ == "__main__":
    main()
