from abc import ABC, abstractmethod
from common.models.lambda_response import LambdaResponse


class DefaultStrategy(ABC):
    def __init__(self, event):
        self.event = event

    @abstractmethod
    def do_validate(self) -> tuple[bool, list]:
        """
        Abstract method to validate the event for the specific strategy.
        Must be implemented by concrete strategy classes.
        """

    @abstractmethod
    def do_operation(self):
        """
        Abstract method to perform the main operation of the strategy.
        Must be implemented by concrete strategy classes.
        """
