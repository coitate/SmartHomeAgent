import os
import time

from dotenv import load_dotenv

from switchbot_client.client import SwitchBotClient

load_dotenv()

SWITCHBOT_TOKEN = os.getenv("SWITCHBOT_TOKEN")
SWITCHBOT_SECRET_KEY = os.getenv("SWITCHBOT_SECRET_KEY")


def main():
    client = SwitchBotClient(token=SWITCHBOT_TOKEN, secret_key=SWITCHBOT_SECRET_KEY)

    print(client.control_device(device_name="ダイニングのライト", command="turnOff"))


if __name__ == "__main__":
    main()
