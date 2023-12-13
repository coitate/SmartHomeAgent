import json
import os
import platform
from enum import Enum
from pathlib import Path

import soundcard
import soundfile
from dotenv import load_dotenv
from openai import OpenAI

from switchbot_client.client import SwitchBotClient

load_dotenv()

SWITCHBOT_TOKEN = os.getenv("SWITCHBOT_TOKEN")
SWITCHBOT_SECRET_KEY = os.getenv("SWITCHBOT_SECRET_KEY")
ORGANIZATION_ID = os.getenv("ORGANIZATION_ID")
API_KEY = os.getenv("API_KEY")


class OS_TYPE(Enum):
    WINDOWS = "Windows"
    MAC = "MAC"
    LINUX = "Linux"


def check_platform() -> OS_TYPE:
    pf = platform.system()
    if pf == "Darwin":
        return OS_TYPE.MAC
    elif pf == "Linux":
        return OS_TYPE.LINUX


def record_sound(sound_file_path: str):
    print("speak your instruction...")

    default_mic = soundcard.default_microphone()

    sample_rate = 48000
    recording_time = 5  # [seconds]
    with default_mic.recorder(samplerate=sample_rate) as mic:
        data = mic.record(numframes=recording_time * sample_rate)

    soundfile.write(sound_file_path, data, sample_rate)


def play_sound(sound_file_path: str):
    print("playing the sound file...")

    default_speaker = soundcard.default_speaker()

    sample_rate = 25000
    with default_speaker.player(samplerate=sample_rate) as sp:
        data, _ = soundfile.read(sound_file_path)
        sp.play(data)


def main():
    os_type = check_platform()
    print(os_type)

    # SwitchBot settings
    sb_client = SwitchBotClient(token=SWITCHBOT_TOKEN, secret_key=SWITCHBOT_SECRET_KEY)

    # OpenAI settings
    ai_client = OpenAI(organization=ORGANIZATION_ID, api_key=API_KEY)
    model = "gpt-3.5-turbo-1106"
    available_functions = {
        f"{sb_client.control_device_with_name.__name__}": sb_client.control_device_with_name
    }
    tools = []
    with open("func_definitions/control_device_with_name.json") as f:
        tools.append(json.load(f))

    messages = [
        {
            "role": "system",
            "content": "You are a smart home agent that can control devices in the home. Any device names must be provided in Japanese. When controlling curtains, turnOn means open and turnOff means close.",
        },
    ]

    # sound file settings
    dir_name = "./soundfile"
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    sound_file_name = "/sound.mp3"
    sound_file_path = Path(dir_name + sound_file_name)

    # Main loop
    while True:
        key = input("Enter to start recording for 5 seconds, q to exit: ")
        if key == "q":
            break
        elif key == "":
            record_sound(sound_file_path)
            with open(sound_file_path, "rb") as f:
                response = ai_client.audio.transcriptions.create(
                    model="whisper-1", file=f
                )
        else:
            print("Invalid key input")
            continue

        prompt = response.text
        messages.append({"role": "user", "content": prompt})
        print("Q:", prompt)

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

            response = ai_client.audio.speech.create(
                model="tts-1", voice="alloy", input=answer
            )
            response.stream_to_file(sound_file_path)

        play_sound(sound_file_path)
        print("A:", answer)

    print("----- Chat history -----")
    for msg in messages:
        msg_dict = dict(msg)
        if msg_dict["content"] is None:
            continue
        if msg["role"] == "system":
            continue

        if msg_dict["role"] == "assistant":
            indent = "\t>>"
        else:
            indent = "\t\t>>"
        print(msg_dict["role"], indent, msg_dict["content"])


if __name__ == "__main__":
    main()
