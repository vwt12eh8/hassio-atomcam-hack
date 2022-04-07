import voluptuous as vol
from homeassistant.components.dhcp import DhcpServiceInfo
from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_HOST, CONF_MAC
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.device_registry import format_mac

from . import DOMAIN, get_ini


class AtomConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1
    host = None

    async def async_step_dhcp(self, discovery_info: DhcpServiceInfo):
        await self.async_set_unique_id(format_mac(discovery_info.macaddress))
        self._abort_if_unique_id_configured(updates={
            CONF_HOST: discovery_info.ip,
        })
        self.host = discovery_info.ip
        return self.async_show_form(step_id="user")

    async def async_step_user(self, user_input: dict = None):
        if user_input:
            self.host = user_input.get(CONF_HOST)
            await self.async_set_unique_id(format_mac(user_input.get(CONF_MAC)))
            self._abort_if_unique_id_configured(updates={
                CONF_HOST: self.host,
            })

        errors = {}
        if self.host and self.unique_id:
            try:
                ini = await get_ini(self.hass, self.host)
                return self.async_create_entry(
                    title=ini["HOSTNAME"],
                    data={
                        CONF_HOST: self.host,
                    },
                )
            except ConfigEntryAuthFailed:
                errors["base"] = "auth_unsupported"

        return self.async_show_form(
            step_id="user",
            errors=errors,
            data_schema=vol.Schema({
                vol.Required(CONF_HOST, default=self.host): str,
                vol.Required(CONF_MAC, default=self.unique_id): str,
            }),
            last_step=True,
        )
