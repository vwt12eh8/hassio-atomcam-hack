from __future__ import annotations

import asyncio
from typing import Callable

from homeassistant.components.update import (UpdateDeviceClass, UpdateEntity,
                                             UpdateEntityFeature)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import (CoordinatorEntity,
                                                      DataUpdateCoordinator)

from . import DOMAIN, Cmd, Ini, exec_cmd, get_device_info


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: Callable):
    async_add_entities([
        FirmUpdate(hass, entry),
        HackUpdate(hass, entry),
    ])


class FirmUpdate(CoordinatorEntity[DataUpdateCoordinator[Ini]], UpdateEntity):
    _attr_device_class = UpdateDeviceClass.FIRMWARE
    _attr_entity_registry_enabled_default = False

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        super().__init__(hass.data[DOMAIN][entry.entry_id]["ini"])
        self._entry = entry
        self._attr_unique_id = self._entry.unique_id + "-appver"

    @property
    def device_info(self):
        return get_device_info(self.hass, self._entry)

    @property
    def installed_version(self):
        return self.coordinator.data["appver"]

    @property
    def name(self):
        return self.coordinator.data["HOSTNAME"] + " Firmware Ver"


class HackUpdate(CoordinatorEntity[DataUpdateCoordinator[Ini]], UpdateEntity):
    _attr_device_class = UpdateDeviceClass.FIRMWARE
    _attr_supported_features = UpdateEntityFeature.INSTALL

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        super().__init__(hass.data[DOMAIN][entry.entry_id]["ini"])
        self._cmd: DataUpdateCoordinator[Cmd] = hass.data[DOMAIN][entry.entry_id]["cmd"]
        self._entry = entry
        self._attr_unique_id = self._entry.unique_id + "-ATOMHACKVER"

    @property
    def available(self):
        return super().available and self._cmd.last_update_success

    @property
    def device_info(self):
        return get_device_info(self.hass, self._entry)

    @property
    def installed_version(self):
        return self.coordinator.data["ATOMHACKVER"]

    @property
    def latest_version(self):
        return self._cmd.data.get("LATESTVER", None) or None

    @property
    def name(self):
        return self.coordinator.data["HOSTNAME"] + " Hack Ver"

    @property
    def release_url(self):
        return f"https://github.com/mnakada/atomcam_tools/releases/tag/Ver.{self.latest_version}"

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        await super().async_added_to_hass()
        self.async_on_remove(
            self._cmd.async_add_listener(self._handle_coordinator_update)
        )

    async def async_install(self, version: str | None, backup: bool, **kwargs):
        session = async_get_clientsession(self.hass)
        await exec_cmd(session, self._entry.data[CONF_HOST], "update")
        await asyncio.sleep(60)

    async def async_update(self):
        """Update the entity.

        Only used by the generic entity update service.
        """
        # Ignore manual update requests if the entity is disabled
        if not self.enabled:
            return

        await asyncio.gather(self.coordinator.async_request_refresh(), self._cmd.async_request_refresh())
