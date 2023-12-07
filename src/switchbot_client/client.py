"""
SwitchBot Client Class
"""

import base64
import hashlib
import hmac
import json
import time
import uuid

import requests


class SwitchBotClient:
    """
    SwichBot Client Class
    """

    def __init__(self, token, secret_key):
        """
        Constructor
        """

        self.__host = "https://api.switch-bot.com"
        self.__token = token
        self.__secret_key = secret_key
        self.__all_devices = {}

        self.__create_device_map()

    def __get_signature(self) -> dict:
        current_time = int(round(time.time() * 1000))
        request_id = uuid.uuid4
        string_to_sign = bytes(f"{self.__token}{current_time}{request_id}", "utf-8")
        secret = bytes(self.__secret_key, "utf-8")

        sign = base64.b64encode(
            hmac.new(secret, msg=string_to_sign, digestmod=hashlib.sha256).digest()
        )

        return {
            "Authorization": self.__token,
            "sign": sign,
            "t": str(current_time),
            "nonce": str(request_id),
        }

    def __create_device_map(self):
        device_list = self.get_device_list()

        for device in device_list:
            self.__all_devices[device["deviceName"]] = {
                "deviceId": device["deviceId"],
                "deviceType": device["deviceType"],
            }

    def __send_command(self, device: str, command: str) -> str:
        device_id = device["deviceId"]

        path = f"/v1.1/devices/{device_id}/commands"
        headers = self.__get_signature()

        payload = {
            "command": command,
        }

        response = requests.post(
            self.__host + path, headers=headers, json=payload, timeout=10.0
        )

        if response.status_code != 200:
            return "Something went wrong"

        return response.json()

    def get_device_list(self) -> list:
        path = "/v1.1/devices"
        headers = self.__get_signature()

        res = requests.get(self.__host + path, headers=headers, timeout=10.0)
        if res.status_code != 200:
            print("Status Code: ", res.status_code)
            return []

        data = res.json()["body"]["deviceList"]

        return data

    def get_infrared_device_list(self) -> list:
        path = "/v1.1/devices"
        headers = self.__get_signature()

        res = requests.get(self.__host + path, headers=headers, timeout=10.0)
        if res.status_code != 200:
            print("Status Code: ", res.status_code)
            return []

        data = res.json()["body"]["infraredRemoteList"]

        return data

    def get_device_status(self, device_id: str) -> str:
        path = f"/v1.1/devices/{device_id}/status"
        headers = self.__get_signature()

        res = requests.get(self.__host + path, headers=headers, timeout=10.0)
        if res.status_code != 200:
            print("Status Code: ", res.status_code)
            return []

        data = res.json()["body"]

        return data

    def control_device(self, device_name: str, command: str):
        print(json.dumps(self.__all_devices, indent=2, ensure_ascii=False))
        if not device_name in self.__all_devices.keys():
            return "Device not found"

        target_device = self.__all_devices[device_name]
        print(target_device)

        return self.__send_command(target_device, command)
