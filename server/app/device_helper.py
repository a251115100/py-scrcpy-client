from typing import Optional, List

from adbutils import adb


class DeviceModel:
    def __init__(
            self,
            device_name: str,
            serial: str,
    ):
        self.device_name = device_name
        self.serial = serial


def query_online_devices() -> List[DeviceModel]:
    device_list = adb.device_list()
    devices = []
    for d in device_list:
        devices.append(DeviceModel(device_name=d.prop.name, serial=d.serial))
    return devices


def query_device_by_name(device_name: str) -> Optional[DeviceModel]:
    device_list = query_online_devices()
    for d in device_list:
        if d.device_name == device_name:
            return d
    return None
