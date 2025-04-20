from neuro_api.command import Action
from neuro_api.api import AbstractNeuroAPI, NeuroAction
import trio
import trio_websocket
import json

from datetime import datetime
import pytz

from os import getenv
from dotenv import load_dotenv

load_dotenv()

all_timezones = pytz.all_timezones

class ClockAPI(AbstractNeuroAPI):
    def __init__(self, game_title: str, connection: trio_websocket.WebSocketConnection | None = None):
        super().__init__(game_title, connection)
    
    async def handle_action(self, action: NeuroAction) -> None:
        if action.data is None:
            print("Didn't find any data.")
            await self.send_action_result(action.id_, False, "You didn't specify anything.")
            return
        
        try:
            action_data = json.loads(action.data)
            timezone = str(action_data.get("timezone"))
            if timezone is None:
                await self.send_action_result(action.id_, False, "You didn't provide a timezone.")
                return
            if timezone not in all_timezones:
                await self.send_action_result(action.id_, False, "You didn't provide a valid (or supported) timezone.")
                return
            time_format = str(action_data.get("format"))
            if time_format is None:
                await self.send_action_result(action.id_, False, "You didn't provide a time format.")
                return
        except (ValueError, TypeError):
            await self.send_action_result(action.id_, False, "Invalid action data.")
            return
        
        # Note: Always send result before executing actions, since the action result is meant to validate stuff.
        await self.send_action_result(action.id_, True)

        # Send off the data to the helper function
        try:
            await self.send_context(f"In the {timezone} format, it is currently {get_formatted_time(timezone, time_format)}.")
            return
        except ValueError:
            await self.send_context("You somehoiw sent something incorrectly. Double-check your inputs and try again.")
            return
        except Exception as e:
            await self.send_context(f"An error occured while trying to check the time\n{e}")


async def clock_game():
    uri = getenv("WEBSOCKET_URI")
    game_title = "Neuro Clock"
    async with trio_websocket.open_websocket_url(uri) as websocket:
        api = ClockAPI(game_title, websocket)
        await api.send_startup_command()
        await api.unregister_actions(["get_current_time"])
        await api.register_actions([Action(
            name="get_current_time",
            description="Get the current time in a timezone",
            schema={
                "type": "object",
                "properties": {
                    "timezone": {"type": "string", "enum": all_timezones},
                    "format": {"type": "string"}
                },
                "required": ["timezone", "format"]
            }
        )])

        while True:
            await api.read_message()


def get_formatted_time(timezone: str, time_format: str) -> str:
    """
    Returns the current time in the specified timezone, formatted as per the given format.

    :param timezone: The timezone string (e.g., 'Asia/Tokyo', 'America/New_York').
    :param time_format: The desired time format (e.g., '%Y-%m-%d %H:%M:%S').
    :return: Formatted time as a string.
    :raise ValueError: When an unknown timezone is entered.
    :raise Exception: Generic errors.
    """
    try:
        # Get the timezone object
        tz = pytz.timezone(timezone)
        
        # Get the current time in the specified timezone
        current_time = datetime.now(tz)
        
        # Format the time
        return current_time.strftime(time_format)
    except pytz.UnknownTimeZoneError:
        raise ValueError(f"Error: Unknown timezone '{timezone}'")
    except Exception as e:
        raise Exception(f"Error: {str(e)}")

if __name__ == "__main__":
    trio.run(clock_game)