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
        self.list_of_actions = {
            "get_current_time": lambda action: self.handle_get_formatted_time(action),
            "get_unix_timestamp": lambda action: self.handle_get_unix_timestamp(action)
        }

    async def handle_action(self, action: NeuroAction) -> None:
        if action.data is None:
            print("Didn't find any data.")
            await self.send_action_result(action.id_, False, "You didn't specify anything.")
            return

        await self.list_of_actions[action.name](action)

    async def handle_get_formatted_time(self, action: NeuroAction) -> None:
        """
        Handles getting the current time, formatted to Neuro's liking.
        """
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
            await self.send_context("You somehow sent something incorrectly. Double-check your inputs and try again.")
            return
        except Exception as e:
            await self.send_context(f"An error occured while trying to check the time\n{e}")

    async def handle_get_unix_timestamp(self, action: NeuroAction) -> None:
        """
        Returns a Unix timestamp of the time input.
        """
        try:
            action_data = json.loads(action.data)
            timezone = str(action_data.get("timezone"))
            if timezone is None:
                await self.send_action_result(action.id_, False, "You didn't provide a timezone.")
                return
            if timezone not in all_timezones:
                await self.send_action_result(action.id_, False, "You didn't provide a valid (or supported) timezone.")
                return
            timestamp = str(action_data.get("timestamp"))
            if timestamp is None:
                await self.send_action_result(action.id_, False, "You didn't provide a timestamp to convert. Make sure it's in %Y-%m-%d %H:%M:%S format when retrying.")
                return
        except (ValueError, TypeError):
            await self.send_action_result(action.id_, False, "Invalid action data.")
            return

        # Note: Always send result before executing actions, since the action result is meant to validate stuff.
        await self.send_action_result(action.id_, True)

        # Send off the data to the helper function
        try:
            await self.send_context(f"The Unix timestamp for {timestamp} in {timezone} is {get_unix_timestamp(timestamp, timezone)}.")
            return
        except ValueError:
            await self.send_context("You somehow sent something incorrectly. Double-check your inputs and try again.")
            return
        except Exception as e:
            await self.send_context(f"An error occured while trying to convert to Unix\n{e}")


list_of_actions = {
    "get_current_time": lambda action: ClockAPI.handle_get_formatted_time(action),
    "get_unix_timestamp": lambda action: ClockAPI.handle_get_unix_timestamp(action)
}


async def clock_game():
    uri = getenv("WEBSOCKET_URI")
    game_title = "Nuru Clock"
    async with trio_websocket.open_websocket_url(uri) as websocket:
        api = ClockAPI(game_title, websocket)
        await api.send_startup_command()
        await api.unregister_actions(list(list_of_actions.keys()))
        await api.register_actions([
            Action(
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
            ),
            Action(
                name="get_unix_timestamp",
                description="Get the Unix timestamp of a time. Requires the timestamp in '%Y-%m-%d %H:%M:%S' format.",
                schema={
                    "type": "object",
                    "properties": {
                        "timezone": {"type": "string", "enum": all_timezones},
                        "timestamp": {"type": "string"}
                    },
                    "required": ["timezone", "timestamp"]
                }
            )
        ])

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


def get_unix_timestamp(timestamp: str, timezone: str) -> int:
    """
    Converts a given timestamp in a specific timezone to a Unix timestamp.

    :param timestamp: The timestamp in '%Y-%m-%d %H:%M:%S' format.
    :param timezone: The timezone string (e.g., 'Asia/Tokyo', 'America/New_York').
    :return: The Unix timestamp of the inputted time.
    :raise ValueError: When an incorrectly formatted string is entered.
    :raise Exception: Generic errors.
    """
    try:
        # Get the timezone object
        tz = pytz.timezone(timezone)

        # Parse the input timestamp into a datetime object
        dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')

        # Localize the datetime object to the specified timezone
        localized_dt = tz.localize(dt)

        # Convert the localized datetime to a Unix timestamp
        unix_timestamp = int(localized_dt.timestamp())

        return unix_timestamp
    except pytz.UnknownTimeZoneError:
        raise ValueError(f"Error: Unknown timezone '{timezone}'")
    except ValueError as e:
        raise ValueError(f"Error: {str(e)}")
    except Exception as e:
        raise Exception(f"Error: {str(e)}")


if __name__ == "__main__":
    trio.run(clock_game)
