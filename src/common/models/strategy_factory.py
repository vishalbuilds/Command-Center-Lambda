from aws_lambda_powertools import Logger

from workflow.amazon_connect.imports import *
from workflow.api_gateway_http.imports import *
from workflow.api_gateway_rest.imports import *
from workflow.functional_url.imports import *
from workflow.s3.imports import *


ALL_INVOCATION_TYPE_LIST = (
    AMAZON_CONNECT + API_GATEWAY_HTTP + API_GATEWAY_REST + FUNCTION_URL + S3
)


LOGGER = Logger(child=True)


class StrategyFactory:
    def __init__(self, event: dict, invoke_type: str):
        self.event = event
        self.invoke_type = invoke_type

        if not self._validate_strategy():
            LOGGER.error("Failed to validate strategy")
            raise ValueError("Failed to validate strategy")

    def _validate_strategy(self) -> bool:
        if self.invoke_type not in globals().keys():
            LOGGER.info("Invalid invoke type", extra={"invoke_type": self.invoke_type})
            return False

        if "request_type" not in self.event:
            LOGGER.info("Missing request_type in event")
            return False

        if self.event.get("request_type") not in ALL_INVOCATION_TYPE_LIST:
            LOGGER.info(
                "Invalid request type",
                extra={"request_type": self.event.get("request_type")},
            )
            return False

        return True

    def _initiate_strategy(self):
        request_type = self.event.get("request_type")
        LOGGER.info("Initiating strategy", extra={"strategy_class": request_type})

        self.strategy_class = globals().get(request_type, None)

        if self.strategy_class is None:
            LOGGER.error(
                "Strategy class not found in globals",
                extra={"strategy_class": request_type},
            )
            raise ValueError(f"Strategy class '{request_type}' not found in globals")

    def _pass_event_to_strategy(self):
        request_type = self.event.get("request_type")
        try:
            self.strategy_class_obj = self.strategy_class(self.event)
            LOGGER.info("Event passed to strategy")
        except Exception:
            LOGGER.exception(
                "Error passing event to strategy",
                extra={"strategy_class": request_type},
            )
            raise

    def execute(self):
        # --- Initiate & pass event ---
        try:
            self._initiate_strategy()
            self._pass_event_to_strategy()
        except Exception:
            LOGGER.exception("Failed to initiate strategy or pass event")
            raise

        # --- Validate ---
        try:
            result, error = self.strategy_class_obj.do_validate()
            if not result:
                LOGGER.error(
                    "Validation failed from strategy class",
                    extra={"error": error},
                )
                raise ValueError(str(error))
        except Exception:
            LOGGER.exception("Unexpected error during strategy validation")
            raise

        # --- Execute ---
        try:
            strategy_response = self.strategy_class_obj.do_operation()
            LOGGER.info(
                "Strategy executed successfully",
                extra={"strategy_response": strategy_response},
            )
            return strategy_response
        except Exception:
            LOGGER.exception("Error during strategy operation")
            raise
