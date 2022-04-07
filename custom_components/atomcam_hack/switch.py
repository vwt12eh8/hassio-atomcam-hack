import json
from typing import Callable, Optional

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import (CoordinatorEntity,
                                                      DataUpdateCoordinator)

from . import DOMAIN, Ini, get_device_info


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: Callable):
    async_add_entities([
        MinAlarmSwitch(hass, entry),
        RtspSwitch(hass, entry),
        RtspAudioSwitch(hass, entry),
        WebhookSwitch(hass, entry),
    ])


class BaseSwitch(CoordinatorEntity[DataUpdateCoordinator[Ini]], SwitchEntity):
    _attr_device_class = SwitchDeviceClass.SWITCH
    _cmd: str
    _name: str
    _setcmd: Optional[str] = None

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        super().__init__(hass.data[DOMAIN][entry.entry_id]["ini"])
        self._entry = entry
        self._attr_unique_id = self._entry.unique_id + f"-{self._cmd}"

    @property
    def device_info(self):
        return get_device_info(self.hass, self._entry)

    @property
    def is_on(self):
        value = self.coordinator.data.get(self._cmd, "off")
        if value == "on":
            return True
        if value == "off":
            return False
        return None

    @property
    def name(self):
        return self.coordinator.data["HOSTNAME"] + f" {self._name}"

    async def async_turn_off(self, **kwargs):
        await self._post("off")

    async def async_turn_on(self, **kwargs):
        await self._post("on")

    async def _post(self, value: str):
        session = async_get_clientsession(self.hass)
        data = self.coordinator.data
        data[self._cmd] = value
        self.coordinator.async_set_updated_data(data)
        await session.post(f"http://{self._entry.data[CONF_HOST]}/cgi-bin/hack_ini.cgi", data=json.dumps(data, separators=(',', ':')))
        if self._setcmd:
            await session.post(f"http://{self._entry.data[CONF_HOST]}/cgi-bin/cmd.cgi", data=f'{{"exec":"{self._setcmd} {value}"}}')


class MinAlarmSwitch(BaseSwitch):
    _attr_entity_category = EntityCategory.CONFIG
    _attr_icon = "mdi:car-speed-limiter"
    _cmd = "MINIMIZE_ALARM_CYCLE"
    _name = "動体検知周期の短縮"


class RtspSwitch(BaseSwitch):
    _attr_entity_category = EntityCategory.CONFIG
    _attr_icon = "mdi:video-outline"
    _cmd = "RTSPSERVER"
    _name = "RTSP"
    _setcmd = "rtspserver"


class RtspAudioSwitch(BaseSwitch):
    _attr_entity_category = EntityCategory.CONFIG
    _attr_entity_registry_enabled_default = False
    _attr_icon = "mdi:microphone-outline"
    _cmd = "RTSP_AUDIO"
    _name = "RTSP 音声"
    _setcmd = "rtspserver"


class WebhookSwitch(BaseSwitch):
    _attr_entity_category = EntityCategory.CONFIG
    _attr_icon = "mdi:webhook"
    _cmd = "WEBHOOK"
    _name = "WebHook"
    _setcmd = "setwebhook"
