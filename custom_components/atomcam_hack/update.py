from __future__ import annotations

import asyncio
from datetime import timedelta
from logging import getLogger
from typing import Callable

from homeassistant.components.update import (UpdateDeviceClass, UpdateEntity,
                                             UpdateEntityFeature)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import (CoordinatorEntity,
                                                      DataUpdateCoordinator)

from . import DOMAIN, Ini, exec_cmd, get_device_info, post_ini

GITHUB_REPO = "https://github.com/mnakada/atomcam_tools"
_LOGGER = getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: Callable):
    if "latest" not in hass.data[DOMAIN][entry.entry_id]:
        session = async_get_clientsession(hass)

        async def _get_latest():
            res = await session.get(f"{GITHUB_REPO}/releases/latest", allow_redirects=False)
            if res.status != 302:
                return
            location = res.headers.get("location", "")
            idx = location.find("Ver.")
            if idx < 0:
                return
            return location[idx + len("Ver."):]

        latest = DataUpdateCoordinator[str](
            hass, _LOGGER,
            name="atomcam_tools/releases/latest",
            update_interval=timedelta(minutes=5),
            update_method=_get_latest,
        )
        hass.data[DOMAIN][entry.entry_id]["latest"] = latest
        hass.async_run_job(latest.async_refresh)

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
    _attr_supported_features = UpdateEntityFeature.INSTALL | UpdateEntityFeature.SPECIFIC_VERSION

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        super().__init__(hass.data[DOMAIN][entry.entry_id]["ini"])
        self.__latest: DataUpdateCoordinator[str] = hass.data[DOMAIN][entry.entry_id]["latest"]
        self._entry = entry
        self._attr_unique_id = self._entry.unique_id + "-ATOMHACKVER"

    @property
    def device_info(self):
        return get_device_info(self.hass, self._entry)

    @property
    def installed_version(self):
        return self.coordinator.data["ATOMHACKVER"]

    @property
    def latest_version(self):
        return self.__latest.data

    @property
    def name(self):
        return self.coordinator.data["HOSTNAME"] + " Hack Ver"

    @property
    def release_url(self):
        return f"{GITHUB_REPO}/releases/tag/Ver.{self.latest_version}"

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        await super().async_added_to_hass()
        self.async_on_remove(
            self.__latest.async_add_listener(self._handle_coordinator_update)
        )

    async def async_install(self, version: str | None, backup: bool, **kwargs):
        session = async_get_clientsession(self.hass)
        host = self._entry.data[CONF_HOST]
        await self.coordinator.async_refresh()

        data = self.coordinator.data
        if version is None:
            data["CUSTOM_ZIP"] = "off"
        else:
            data["CUSTOM_ZIP"] = "on"
            data["CUSTOM_ZIP_URL"] = f"{GITHUB_REPO}/releases/download/Ver.{version}/atomcam_tools.zip"

        await post_ini(session, host, self.coordinator)
        await exec_cmd(session, host, "update")
        await asyncio.sleep(60)

    async def async_update(self):
        """Update the entity.

        Only used by the generic entity update service.
        """
        # Ignore manual update requests if the entity is disabled
        if not self.enabled:
            return

        await asyncio.gather(self.coordinator.async_request_refresh(), self.__latest.async_request_refresh())
