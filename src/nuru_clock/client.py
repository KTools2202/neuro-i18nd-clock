from __future__ import annotations

import os
import json
from typing import Final

import trio
from neuro_api.api import NeuroAction
from neuro_api.trio_ws import TrioNeuroAPI
import trio_websocket
from dotenv import load_dotenv
from jsonschema import validate, ValidationError

from nuru_clock.clocks import GetFormattedTimeAction, GetUnixTimestampAction
from nuru_clock.utils import log

load_dotenv()

WEBSOCKET_ENV_VAR: Final = "WEBSOCKET_URI"  # "NEURO_SDK_WS_URL"
DEFAULT_WEBSOCKET: Final = "ws://localhost:8000"


class ClockAPI(TrioNeuroAPI):
    def __init__(self, game_title: str, connection: trio_websocket.WebSocketConnection | None = None):
        super().__init__(game_title, connection)
        self.actions = [
            GetFormattedTimeAction(),
            GetUnixTimestampAction()
        ]
        log("INFO", f"ClockAPI initialized with game title: {game_title}")

    def connect(self, value: trio_websocket.WebSocketConnection | None) -> None:
        log("DEBUG", "Setting WebSocket connection.")
        super().connect(value)

    async def handle_action(self, action: NeuroAction) -> None:
        log("INFO", f"Handling action: {action.name}")
        for act in self.actions:
            if act.name == action.name:
                try:
                    # Validate the incoming data against the action's schema
                    action_data = json.loads(action.data) if action.data else {}
                    validate(instance=action_data, schema=act.schema)
                    log("DEBUG", f"Schema validation passed for action: {action.name}")

                    # Perform the action
                    success, result = await act.perform_action(action)
                    log("INFO", f"Action '{action.name}' performed with result: {result}")
                    await self.send_action_result(action.id_, success, result)
                except ValidationError as e:
                    log("WARNING", f"Schema validation failed for action '{action.name}': {e.message}")
                    await self.send_action_result(action.id_, False, f"Invalid data: {e.message}")
                except Exception as e:
                    log("ERROR", f"Error occurred while handling action '{action.name}': {e}")
                    await self.send_action_result(action.id_, False, f"An error occurred: {e}")
                return
        log("WARNING", f"Unknown action: {action.name}")
        await self.send_action_result(action.id_, False, "Unknown action.")

    async def clock_game(self) -> None:
        websocket_url = os.environ.get(WEBSOCKET_ENV_VAR, DEFAULT_WEBSOCKET)
        log("INFO", f"Connecting to WebSocket Server: {websocket_url}")
        if not websocket_url or not websocket_url.startswith(("ws://", "wss://")):
            log("ERROR", "Invalid WebSocket URL. Ensure it starts with 'ws://' or 'wss://'.")
            raise ValueError("Invalid WebSocket URL. Ensure it starts with 'ws://' or 'wss://'.")
        async with trio_websocket.open_websocket_url(websocket_url) as websocket:
            self.connect(websocket)
            log("INFO", "WebSocket connection established.")
            await self.send_startup_command()
            await self.unregister_actions([act.name for act in self.actions])
            await self.register_actions([act.get_action() for act in self.actions])
            log("INFO", "Actions registered successfully.")
            while True:
                await self.read_message()


def main() -> None:
    clock_api = ClockAPI("Nuru Clock")
    trio.run(clock_api.clock_game)


if __name__ == "__main__":
    main()
