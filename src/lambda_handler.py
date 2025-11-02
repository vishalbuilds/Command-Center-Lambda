
from common.models.strategy_factory import StrategyFactory
from common.models.lambda_response import LambdaResponse
from common.models.event_sanitizer import EventSanitizer
from common.models.trace_id import TraceId
from common.models.find_invocation_source import get_invocation_source,extract_event_data
from common.models.logger import Logger


LOGGER = Logger(__name__)

def lambda_handler(event, context) ->LambdaResponse:

    invocation_source=None
    #init trace id process
    try:
        LOGGER.info(f"Lambda handler initialized with context: {context}.")
        LOGGER.init_context(context)
        TraceId.init(context)
        LOGGER.add_metadata("trace_id", TraceId.get())
    except Exception as e:
        LOGGER.add_tempdata("error",str(e))
        LOGGER.error(f"Error in processing Trace Id: {e}")
        return LambdaResponse.error(message=str(e))
    
    #init checking event source and extracting usefull event
    try:
        invocation_source=get_invocation_source(event)
        LOGGER.add_metadata("invocation_source", invocation_source)
        event=extract_event_data(event,invocation_source)
    except Exception as e:
        LOGGER.add_tempdata("errror",str(e))
        LOGGER.error(f"Error in processing event from function url invocation: {e}")
        return LambdaResponse.error(message=str(e))
    

    #init Event Sanitizer to remove PII information
    try:
        LOGGER.info("Processing event sanitizer to remove sensitive data")
        event = EventSanitizer(event).data()
    except Exception as e:
        LOGGER.add_tempdata("error",str(e))
        LOGGER.error(f"Error in processing Event Sanitizer: {e}")
        return LambdaResponse.error(message=str(e))
    
    
    # Use StrategyFactory to choose and run strategy
    try:
        LOGGER.info(f"Processing event: {event}")
        LOGGER.add_metadata("event", event)

        response = StrategyFactory(event,invocation_source).execute()

        LOGGER.info(f"Strategy response: {response}")
        LOGGER.add_metadata("response", response)
        #final return from lambda
        return LambdaResponse.success(message="Strategy executed successfully", data=response)
    except Exception as e:
        LOGGER.add_tempdata("error",str(e))
        LOGGER.error(f"Error in processing final execution: {e}")
        return LambdaResponse.error(message=str(e))

