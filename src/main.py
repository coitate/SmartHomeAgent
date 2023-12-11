import json
import os

from dotenv import load_dotenv

from switchbot_client.client import SwitchBotClient

load_dotenv()

SWITCHBOT_TOKEN = os.getenv("SWITCHBOT_TOKEN")
SWITCHBOT_SECRET_KEY = os.getenv("SWITCHBOT_SECRET_KEY")


def main():
    client = SwitchBotClient(token=SWITCHBOT_TOKEN, secret_key=SWITCHBOT_SECRET_KEY)

    print(json.dumps(client.get_name_based_devices(), indent=2, ensure_ascii=False))

    device_name = "ダイニングのライト"
    print(client.get_device_id_with_name(device_name=device_name))
    print(client.get_device_status_with_name(device_name=device_name))
    print(client.control_device_with_name(device_name=device_name, command="toggle"))
    print(client.get_device_status_with_name(device_name=device_name))


if __name__ == "__main__":
    main()
