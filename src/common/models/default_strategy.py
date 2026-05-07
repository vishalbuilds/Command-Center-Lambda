from abc import ABC, abstractmethod


class DefaultStrategy(ABC):
    def __init__(self, event):
        self.event = event

    @abstractmethod
    def do_validate(self):
        """
        Abstract method to validate the event for the specific strategy.
        Must be implemented by concrete strategy classes.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement do_validate"
        )

    @abstractmethod
    def do_operation(self):
        """
        Abstract method to perform the main operation of the strategy.
        Must be implemented by concrete strategy classes.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement do_operation"
        )
