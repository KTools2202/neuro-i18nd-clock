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
            if action.data is None:
                await self.send_action_result(action.id_, False, "No action data provided.")
                return
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

        # Always send result (i.e. validation) before executing action.
        await self.send_action_result(action.id_, True)

        try:
            await self.send_context(
                f"In the {timezone} format, it is currently {get_formatted_time(timezone, time_format)}."
            )
            return
        except ValueError:
            await self.send_context("Double-check your inputs and try again.")
            return
        except Exception as e:
            await self.send_context(f"An error occurred: {e}")

    async def handle_get_unix_timestamp(self, action: NeuroAction) -> None:
        """
        Returns a Unix timestamp of the time input.
        """
        try:
            if action.data is None:
                await self.send_action_result(action.id_, False, "No action data provided.")
                return
            action_data = json.loads(action.data)
            timezone = str(action_data.get("timezone"))
            if timezone is None:
                await self.send_action_result(action.id_, False, "You didn't provide a timezone.")
                return
            if timezone not in all_timezones:
                await self.send_action_result(action.id_, False, "Invalid timezone provided.")
                return
            timestamp = str(action_data.get("timestamp"))
            if timestamp is None:
                await self.send_action_result(
                    action.id_,
                    False,
                    "Timestamp missing. Use '%Y-%m-%d %H:%M:%S' format."
                )
                return
        except (ValueError, TypeError):
            await self.send_action_result(action.id_, False, "Invalid action data.")
            return

        # Always send validation result before performing an action.
        await self.send_action_result(action.id_, True)

        try:
            await self.send_context(
                f"The Unix timestamp for {timestamp} in {timezone} is {get_unix_timestamp(timestamp, timezone)}."
            )
            return
        except ValueError:
            await self.send_context("Double-check your inputs and try again.")
            return
        except Exception as e:
            await self.send_context(f"An error occurred: {e}")


async def clock_game():
    uri = getenv("WEBSOCKET_URI")
    game_title = "Nuru Clock"
    async with trio_websocket.open_websocket_url(uri) as websocket:
        api = ClockAPI(game_title, websocket)
        await api.send_startup_command()
        # Unregister using the keys from the instance's actions, not a global dictionary.
        await api.unregister_actions(list(api.list_of_actions.keys()))
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
                description="Get the Unix timestamp (timestamp must be in '%Y-%m-%d %H:%M:%S' format).",
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
        tz = pytz.timezone(timezone)
        current_time = datetime.now(tz)
        return current_time.strftime(time_format)
    except pytz.UnknownTimeZoneError:
        raise ValueError(f"Unknown timezone: {timezone}")
    except Exception as e:
        raise Exception(f"Error: {e}")


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
        tz = pytz.timezone(timezone)
        dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        localized_dt = tz.localize(dt)
        return int(localized_dt.timestamp())
    except pytz.UnknownTimeZoneError:
        raise ValueError(f"Unknown timezone: {timezone}")
    except ValueError as e:
        raise ValueError(f"Error: {e}")
    except Exception as e:
        raise Exception(f"Error: {e}")


def main():
    trio.run(clock_game)


if __name__ == "__main__":
    main()
