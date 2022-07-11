from typing import Callable

from homeassistant.components.button import ButtonDeviceClass, ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import (CoordinatorEntity,
                                                      DataUpdateCoordinator)

from . import DOMAIN, Ini, exec_cmd, get_device_info


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: Callable):
    async_add_entities([
        EraseButton(hass, entry),
        RebootButton(hass, entry),
    ])


class ExecButton(CoordinatorEntity[DataUpdateCoordinator[Ini]], ButtonEntity):
    _attr_has_entity_name = True
    _cmd: str

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        super().__init__(hass.data[DOMAIN][entry.entry_id]["ini"])
        self._entry = entry
        self._attr_unique_id = self._entry.unique_id + f"-{self._cmd}"

    @property
    def device_info(self):
        return get_device_info(self.hass, self._entry)

    async def async_press(self):
        session = async_get_clientsession(self.hass)
        await exec_cmd(session, self._entry.data[CONF_HOST], self._cmd)


class EraseButton(ExecButton):
    _attr_entity_category = EntityCategory.CONFIG
    _attr_entity_registry_enabled_default = False
    _attr_icon = "mdi:folder-remove-outline"
    _cmd = "sderase"
    _attr_name = "SD-Card消去"


class RebootButton(ExecButton):
    _attr_entity_category = EntityCategory.CONFIG
    _attr_entity_registry_enabled_default = False
    _attr_device_class = ButtonDeviceClass.RESTART
    _cmd = "reboot"
    _attr_name = "リブート"
