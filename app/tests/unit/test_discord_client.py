import asyncio

import pytest

# Skip the tests if the optional discord dependency isn't available in the environment
pytest.importorskip("discord")

import app.services.discord as dc


def test_on_ready_is_coroutine():
    """Ensure the `on_ready` handler is an async coroutine."""
    assert asyncio.iscoroutinefunction(dc.on_ready)


def test_ping_command_registered():
    """The `ping` command should be registered on the bot."""
    cmd = dc.bot.get_command("ping")
    assert cmd is not None
    assert callable(cmd.callback)
    assert cmd.name == "ping"
