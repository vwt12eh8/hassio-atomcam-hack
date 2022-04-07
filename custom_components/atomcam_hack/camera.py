from typing import Callable

from homeassistant.components.camera import SUPPORT_STREAM, Camera
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import (CoordinatorEntity,
                                                      DataUpdateCoordinator)

from . import DOMAIN, Ini, get_device_info


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: Callable):
    async_add_entities([AtomCam(hass, entry)])


class AtomCam(CoordinatorEntity[DataUpdateCoordinator[Ini]], Camera):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        CoordinatorEntity.__init__(
            self, hass.data[DOMAIN][entry.entry_id]["ini"])
        Camera.__init__(self)
        self._entry = entry
        self._attr_unique_id = self._entry.unique_id

    @property
    def device_info(self):
        return get_device_info(self.hass, self._entry)

    @property
    def is_streaming(self):
        return self.coordinator.data.get("RTSPSERVER", "") == "on"

    @property
    def name(self):
        return self.coordinator.data["HOSTNAME"]

    @property
    def supported_features(self):
        if self.is_streaming:
            return SUPPORT_STREAM
        return 0

    async def async_camera_image(self, width: int = None, height: int = None):
        session = async_get_clientsession(self.hass)
        res = await session.get(f"http://{self._entry.data[CONF_HOST]}/cgi-bin/get_jpeg.cgi")
        if res.status != 200:
            return None
        return await res.read()

    async def stream_source(self):
        return f"rtsp://{self._entry.data[CONF_HOST]}:8554/unicast"
