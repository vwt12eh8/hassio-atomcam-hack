import asyncio
from datetime import timedelta
from logging import getLogger
from typing import TypedDict

from aiohttp.helpers import BasicAuth
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (DataUpdateCoordinator,
                                                      UpdateFailed)

DOMAIN = "atomcam_hack"
_LOGGER = getLogger(__name__)
_PLATFORMS = {
    Platform.BUTTON,
    Platform.CAMERA,
    Platform.SWITCH,
    Platform.UPDATE,
}


class Cmd(TypedDict):
    LATESTVER: str
    TIMESTAMP: str
    MOTORPOS: str


class Ini(TypedDict):
    appver: str
    ATOMHACKVER: str
    HOSTNAME: str
    PRODUCT_MODEL: str


def get_device_info(hass: HomeAssistant, entry: ConfigEntry):
    ini: Ini = hass.data[DOMAIN][entry.entry_id]["ini"].data
    return DeviceInfo(
        configuration_url=f"http://{entry.data[CONF_HOST]}",
        connections={(CONNECTION_NETWORK_MAC, entry.unique_id)},
        identifiers={(DOMAIN, entry.unique_id)},
        manufacturer="ATOM tech Inc.",
        model=ini.get("PRODUCT_MODEL", None),
        name=ini.get("HOSTNAME", None),
        sw_version=ini.get("appver", None),
    )


async def _get_base(hass: HomeAssistant, host: str, name: str, auth: BasicAuth = None):
    session = async_get_clientsession(hass)
    res = await session.get(f"http://{host}/cgi-bin/{name}", auth=auth)
    if res.status == 401:
        raise UpdateFailed("ログイン認証には対応していません")
    if res.status != 200:
        raise UpdateFailed(f"status: {res.status}")
    res = await res.text()

    d = Ini()
    for line in res.split("\n"):
        i = line.find("=")
        if i == -1:
            continue
        d[line[0:i]] = line[i + 1:]
    return d


async def get_ini(hass: HomeAssistant, host: str, auth: BasicAuth = None):
    return await _get_base(hass, host, "hack_ini.cgi", auth)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    async def _get_cmd():
        return await _get_base(hass, entry.data[CONF_HOST], "cmd.cgi")

    async def _get_ini():
        return await get_ini(hass, entry.data[CONF_HOST])

    cmd = DataUpdateCoordinator(hass, _LOGGER, name="cmd.cgi", update_interval=timedelta(
                                minutes=5), update_method=_get_cmd)
    ini = DataUpdateCoordinator(hass, _LOGGER, name="hack_ini.cgi",
                                update_interval=timedelta(seconds=5), update_method=_get_ini)
    await asyncio.gather(ini.async_config_entry_first_refresh(), cmd.async_config_entry_first_refresh())
    hass.data[DOMAIN][entry.entry_id] = {
        "cmd": cmd,
        "ini": ini,
    }

    hass.config_entries.async_setup_platforms(entry, _PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)
