from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext


from common.models.strategy_factory import StrategyFactory
from common.models.lambda_response import LambdaResponse
from common.models.event_sanitizer import EventSanitizer

# from common.models.trace_id import TraceId
from common.models.find_invocation_source import (
    get_invocation_source,
    extract_event_data,
)

LOGGER = Logger()


@LOGGER.inject_lambda_context(log_event=True)
def lambda_handler(event, context: LambdaContext) -> LambdaResponse:

    invocation_source = None

    # init checking event source and extracting usefull event
    try:
        invocation_source = get_invocation_source(event)
        LOGGER.info(
            "Invocation source received", extra={"invocation_source": invocation_source}
        )
        event = extract_event_data(event, invocation_source)
    except Exception as e:
        LOGGER.exception("Error in processing event from function url invocation")
        return LambdaResponse.error(message=str(e))

    # init Event Sanitizer to remove PII information, if isSanitizationEnabled is true and maskText is set with text type required to redact
    try:
        LOGGER.info(
            "Processing event sanitizer to remove sensitive data",
            extra={"event": event},
        )
        event = EventSanitizer(event).get_sanitized_data()
    except Exception as e:
        LOGGER.exception("Error in processing Event Sanitizer")
        return LambdaResponse.error(message=str(e))

    # Use StrategyFactory to choose and run strategy
    try:
        LOGGER.info("Processing strategy", extra={"event": event})
        response = StrategyFactory(event, invocation_source).execute()

        LOGGER.info("Strategy response", extra={"response": response})

        # final return from lambda
        return LambdaResponse.success(
            message="Strategy executed successfully", data=response
        )
    except Exception as e:
        LOGGER.exception("Error in processing final execution")
        return LambdaResponse.error(message=str(e))
