"""
SwitchBot Client Class
"""

import base64
import datetime
import hashlib
import hmac
import time
import uuid
from enum import Enum

import requests


class DeviceType(Enum):
    ALL = 0  # All
    SB = "deviceList"  # SwitchBot Device
    IR = "infraredRemoteList"  # Infrared Device


class SwitchBotClient:
    def __init__(self, token, secret_key):
        self.__host = "https://api.switch-bot.com"
        self.__token = token
        self.__secret_key = secret_key
        self.__last_request_time = None
        self.__all_devices = self.__get_all_devices()
        self.__all_name_based_devices = self.__get_all_name_based_devices()

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

    def __sleep_api_call(self, current: datetime.datetime) -> None:
        # TODO: move to common process when api calling
        wait_time = 1
        if self.__last_request_time is None:
            self.__last_request_time = current - datetime.timedelta(seconds=wait_time)

        while True:
            if current - self.__last_request_time >= datetime.timedelta(
                seconds=wait_time
            ):
                break
            time.sleep(wait_time / 2.0)
            current = datetime.datetime.now()

        self.__last_request_time = current

    def __get_all_devices(self) -> dict:
        path = "/v1.1/devices"
        headers = self.__get_signature()

        self.__sleep_api_call(datetime.datetime.now())

        res = requests.get(url=self.__host + path, headers=headers, timeout=10.0)
        if res.status_code != 200:
            print("Status Code: ", res.status_code)
            print("cannot get all devices")
            return []

        return res.json()["body"]

    def __get_all_name_based_devices(self) -> dict:
        all_devices = self.__all_devices
        sb_devices = all_devices[DeviceType.SB.value]
        ir_devices = all_devices[DeviceType.IR.value]

        name_based_devices = {}

        for device in sb_devices:
            device_name = device.pop("deviceName")
            name_based_devices[device_name] = device

        for device in ir_devices:
            device_name = device.pop("deviceName")
            name_based_devices[device_name] = device

        return name_based_devices

    def __send_command(self, device_id: str, command: str) -> dict:
        path = f"/v1.1/devices/{device_id}/commands"
        headers = self.__get_signature()

        payload = {
            "command": command,
        }

        self.__sleep_api_call(datetime.datetime.now())

        response = requests.post(
            self.__host + path, headers=headers, json=payload, timeout=10.0
        )

        if response.status_code != 200:
            return "Something went wrong"

        return response.json()

    def get_devices(self, device_type: DeviceType) -> dict:
        if device_type == DeviceType.ALL:
            return self.__all_devices
        return self.__all_devices[device_type.value]

    def get_name_based_devices(self) -> dict:
        return self.__all_name_based_devices

    def get_device_id_with_name(self, device_name: str) -> str:
        return self.__all_name_based_devices[device_name]["deviceId"]

    def get_device_status_with_id(self, device_id: str) -> dict:
        path = f"/v1.1/devices/{device_id}/status"
        headers = self.__get_signature()

        self.__sleep_api_call(datetime.datetime.now())

        res = requests.get(self.__host + path, headers=headers, timeout=10.0)
        if res.status_code != 200:
            print("Status Code: ", res.status_code)
            return []

        return res.json()["body"]

    def get_device_status_with_name(self, device_name: str) -> dict:
        device_id = self.get_device_id_with_name(device_name)
        return self.get_device_status_with_id(device_id)

    def control_device_with_name(self, device_name: str, command: str) -> dict:
        device_id = self.get_device_id_with_name(device_name)
        return self.__send_command(device_id, command)
