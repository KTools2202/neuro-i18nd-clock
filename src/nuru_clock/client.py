from neuro_api.api import AbstractNeuroAPI, NeuroAction
import trio_websocket
from os import getenv
from dotenv import load_dotenv
from jsonschema import validate, ValidationError
from .clocks import GetFormattedTimeAction, GetUnixTimestampAction
from .utils import log
import json

load_dotenv()


class ClockAPI(AbstractNeuroAPI):
    def __init__(self, game_title: str, connection: trio_websocket.WebSocketConnection | None = None):
        super().__init__(game_title, connection)
        self._connection = connection  # Use a private attribute for the connection
        self.actions = [
            GetFormattedTimeAction(),
            GetUnixTimestampAction()
        ]
        log("INFO", f"ClockAPI initialized with game title: {game_title}")

    @property
    def connection(self):
        return self._connection

    @connection.setter
    def connection(self, value):
        log("DEBUG", "Setting WebSocket connection.")
        self._connection = value

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

    async def clock_game(self):
        uri = getenv("WEBSOCKET_URI")
        log("INFO", f"Connecting to WebSocket URI: {uri}")
        if not uri or not uri.startswith(("ws://", "wss://")):
            log("ERROR", "Invalid WebSocket URI. Ensure it starts with 'ws://' or 'wss://'.")
            raise ValueError("Invalid WebSocket URI. Ensure it starts with 'ws://' or 'wss://'.")
        async with trio_websocket.open_websocket_url(uri) as websocket:
            self.connection = websocket
            log("INFO", "WebSocket connection established.")
            await self.send_startup_command()
            await self.unregister_actions([act.name for act in self.actions])
            await self.register_actions([act.get_action() for act in self.actions])
            log("INFO", "Actions registered successfully.")
            while True:
                await self.read_message()