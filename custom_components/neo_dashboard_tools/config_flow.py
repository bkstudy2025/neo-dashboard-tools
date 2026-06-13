"""Config + options flow for Neo Dashboard Tools.

The options flow (Configure button in Devices & Services) is the central
place to add / remove dashboard modules.
"""
from __future__ import annotations

import os
import re

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .const import DOMAIN, MODULES_DIR, SIGNAL_UPDATE

_RE_REGISTER = re.compile(r"""registerCard\(\s*["'`]([\w-]+)["'`]""")


def _modules_dir(hass) -> str:
    path = hass.config.path(MODULES_DIR)
    os.makedirs(path, exist_ok=True)
    return path


def _safe(name: str) -> str:
    name = "".join(c for c in (name or "") if c.isalnum() or c in "-_")
    return (name or "module")[:64]


def _module_names(hass) -> list[str]:
    import glob

    return sorted(
        os.path.splitext(os.path.basename(p))[0]
        for p in glob.glob(os.path.join(_modules_dir(hass), "*.js"))
    )


def _write_module(hass, name: str, code: str) -> None:
    with open(os.path.join(_modules_dir(hass), f"{_safe(name)}.js"), "w", encoding="utf-8") as fh:
        fh.write(code)


def _delete_module(hass, name: str) -> None:
    path = os.path.join(_modules_dir(hass), f"{_safe(name)}.js")
    if os.path.exists(path):
        os.remove(path)


class NeoDashboardToolsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Single-instance config flow — just creates the entry."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()
        return self.async_create_entry(title="Neo Dashboard Tools", data={})

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return NeoOptionsFlow()


class NeoOptionsFlow(config_entries.OptionsFlow):
    """Add / remove modules from Devices & Services → Configure."""

    async def async_step_init(self, user_input=None):
        return self.async_show_menu(step_id="init", menu_options=["add_module", "remove_module"])

    async def async_step_add_module(self, user_input=None):
        errors = {}
        if user_input is not None:
            code = (user_input.get("code") or "").strip()
            name = (user_input.get("name") or "").strip()
            if not name:
                match = _RE_REGISTER.search(code)
                name = match.group(1) if match else "module"
            if not code:
                errors["code"] = "empty_code"
            else:
                await self.hass.async_add_executor_job(_write_module, self.hass, name, code)
                async_dispatcher_send(self.hass, SIGNAL_UPDATE)
                return self.async_create_entry(title="", data={})

        schema = vol.Schema(
            {
                vol.Optional("name"): selector.TextSelector(),
                vol.Required("code"): selector.TextSelector(
                    selector.TextSelectorConfig(multiline=True)
                ),
            }
        )
        return self.async_show_form(step_id="add_module", data_schema=schema, errors=errors)

    async def async_step_remove_module(self, user_input=None):
        names = await self.hass.async_add_executor_job(_module_names, self.hass)
        if not names:
            return self.async_abort(reason="no_modules")
        if user_input is not None:
            await self.hass.async_add_executor_job(_delete_module, self.hass, user_input["module"])
            async_dispatcher_send(self.hass, SIGNAL_UPDATE)
            return self.async_create_entry(title="", data={})

        schema = vol.Schema(
            {
                vol.Required("module"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=names, mode=selector.SelectSelectorMode.DROPDOWN
                    )
                )
            }
        )
        return self.async_show_form(step_id="remove_module", data_schema=schema)
