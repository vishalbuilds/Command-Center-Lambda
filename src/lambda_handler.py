from common.strategy_factory import StrategyFactory
from common.response_builder import ResponseBuilder
from common.event_sanitizer import EventSanitizer
from common.logger import Logger

LOGGER = Logger(__name__)

def lambda_handler(event, context) ->ResponseBuilder:

    LOGGER.info(f"Lambda handler started with {event}.")

    sanitizer = EventSanitizer(event)

    clean_event = sanitizer.data  # get sanitized dictionary
    
    LOGGER.info(f"Sanitized event: {clean_event}"   )
    
    # Use StrategyFactory to choose and run strategy
    strategy = StrategyFactory(clean_event)
    try:
        response = strategy.execute()
        LOGGER.info(f"Strategy response: {response}")
        # Build final Lambda response
        final_response = ResponseBuilder().success(data=response)
    except Exception as e:
        LOGGER.error(f"Error executing strategy: {e}")
        final_response = ResponseBuilder().error(message=str(e))
    LOGGER.info(f"Final response: {final_response}")
    
    return final_response
