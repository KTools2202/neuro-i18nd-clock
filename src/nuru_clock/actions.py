from abc import ABC, abstractmethod
from typing import Callable, Coroutine, Any, Optional
from neuro_api.command import Action
from neuro_api.api import NeuroAction


class AbstractAction(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def desc(self) -> str:
        pass

    @property
    @abstractmethod
    def schema(self) -> dict[str, object]:
        pass

    def get_action(self) -> Action:
        """
        Returns an Action object containing the name, description, and schema of the action.
        """
        return Action(self.name, self.desc, self.schema)

    def get_handler(self) -> Callable[[NeuroAction], Coroutine[Any, Any, tuple[bool, Optional[str]]]]:
        """
        Returns the handler function for the action.
        """
        return self.perform_action

    @abstractmethod
    async def perform_action(self, action: NeuroAction) -> tuple[bool, Optional[str]]:
        """
        Carries out the action.
        """
