import json
import pytz
from datetime import datetime
from neuro_api.api import NeuroAction
from .actions import AbstractAction
from typing import Optional
from .utils import log

all_timezones = pytz.all_timezones


class GetFormattedTimeAction(AbstractAction):
    @property
    def name(self) -> str:
        return "get_current_time"

    @property
    def desc(self) -> str:
        return "Get the current time in a timezone"

    @property
    def schema(self) -> dict[str, object]:
        return {
            "type": "object",
            "properties": {
                "timezone": {"type": "string", "enum": all_timezones},
                "format": {"type": "string"}
            },
            "required": ["timezone", "format"]
        }

    async def perform_action(self, action: NeuroAction) -> tuple[bool, Optional[str]]:
        log("INFO", f"Performing action '{self.name}' with data: {action.data}")
        try:
            if action.data is None:
                log("WARNING", "No action data provided.")
                return False, "No action data provided."
            action_data = json.loads(action.data)
            timezone = str(action_data.get("timezone"))
            if timezone not in all_timezones:
                log("WARNING", f"Invalid timezone provided: {timezone}")
                return False, "Invalid timezone provided."
            time_format = str(action_data.get("format"))
            formatted_time = get_formatted_time(timezone, time_format)
            log("INFO", f"Formatted time: {formatted_time}")
            return True, f"In the {timezone} format, it is currently {formatted_time}."
        except Exception as e:
            log("ERROR", f"Error occurred while performing action '{self.name}': {e}")
            return False, f"An error occurred: {e}"


class GetUnixTimestampAction(AbstractAction):
    @property
    def name(self) -> str:
        return "get_unix_timestamp"

    @property
    def desc(self) -> str:
        return "Get the Unix timestamp of a time"

    @property
    def schema(self) -> dict[str, object]:
        return {
            "type": "object",
            "properties": {
                "timezone": {"type": "string", "enum": all_timezones},
                "timestamp": {"type": "string"}
            },
            "required": ["timezone", "timestamp"]
        }

    async def perform_action(self, action: NeuroAction) -> tuple[bool, Optional[str]]:
        log("INFO", f"Performing action '{self.name}' with data: {action.data}")
        try:
            if action.data is None:
                log("WARNING", "No action data provided.")
                return False, "No action data provided."
            action_data = json.loads(action.data)
            timezone = str(action_data.get("timezone"))
            timestamp = str(action_data.get("timestamp"))
            unix_timestamp = get_unix_timestamp(timestamp, timezone)
            log("INFO", f"Unix timestamp: {unix_timestamp}")
            return True, f"The Unix timestamp for {timestamp} in {timezone} is {unix_timestamp}."
        except Exception as e:
            log("ERROR", f"Error occurred while performing action '{self.name}': {e}")
            return False, f"An error occurred: {e}"


def get_formatted_time(timezone: str, time_format: str) -> str:
    log("DEBUG", f"Getting formatted time for timezone: {timezone}, format: {time_format}")
    tz = pytz.timezone(timezone)
    current_time = datetime.now(tz)
    return current_time.strftime(time_format)


def get_unix_timestamp(timestamp: str, timezone: str) -> int:
    log("DEBUG", f"Getting Unix timestamp for timezone: {timezone}, timestamp: {timestamp}")
    tz = pytz.timezone(timezone)
    dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
    localized_dt = tz.localize(dt)
    return int(localized_dt.timestamp())