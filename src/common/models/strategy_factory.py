from common.models.logger import Logger
from common.models.lambda_response import LambdaResponse
from workflow.amazon_connect.imports import *
from workflow.api_gateway_http.imports import *
from workflow.api_gateway_rest.imports import *
from workflow.functional_url.imports import *
from workflow.s3.imports import *


ALL_INVOKE_TYPE_LIST=AMAZON_CONNECT+API_GATEWAY_HTTP+API_GATEWAY_REST+FUNCTION_URL+S3

LOGGER = Logger(__name__)


class StrategyFactory:
    def __init__(self, event:dict, invoke_type: str):
        self.event = event
        self.invoke_type=invoke_type

        if not self._validate_strategy():
            LOGGER.error(f"Failed in validate strategy")
            raise Exception(f"Failed in validate strategy")
        

    #validation
    def _validate_strategy(self):
        if self.invoke_type not in globals().keys():
            LOGGER.add_tempdata("Invalid invoke strategy type", self.invoke_type)
            return False

        if "request_type" not in self.event:
            LOGGER.add_tempdata("Event must contain request_type", self.event)
            return False

        if self.event.get("request_type") not in ALL_INVOKE_TYPE_LIST:
            LOGGER.add_tempdata("Invalid strategy", self.event.get('request_type'))
            return False
        return True
            
    #initiating the strategy and call the invocation class 
    def _initiate_strategy(self):
        try:
            request_type = self.event.get("request_type")
            self.strategy_class = globals().get(request_type,None)
            LOGGER.info(f"Initiating strategy: {request_type}")
            
            if self.strategy_class is None:
                LOGGER.add_tempdata("Strategy class not found in globals",request_type)
                raise Exception(f"Strategy class '{request_type}' not found in globals")

        except Exception as e:
            LOGGER.add_tempdata("error", str(e))
            LOGGER.error(f"Error initiating strategy: {e}")
            raise Exception(f"Failed to initiate strategy: {e}")
             

    def _pass_event_to_strategy(self):
        try:
            self.strategy_class_obj=self.strategy_class(self.event)
            LOGGER.info(f"Event passed to strategy: {self.event}")
        except Exception as e:
            LOGGER.add_tempdata("error", str(e))
            LOGGER.error(f"Error passing event to strategy: {e}")


    def execute(self):
        try:
            self._initiate_strategy()
            self._pass_event_to_strategy()
            if not self.strategy_class_obj.do_validate():
                LOGGER.add_tempdata("validation failed from called strategy_class",self.strategy_class_obj)
                raise Exception("validation failed from called strategy_class")
        except Exception as e:
                LOGGER.add_tempdata("error",str(e))
                LOGGER.error(f"Error in validation from called strategy_class: {e}")
                return LambdaResponse.error(message=str(e))
        
        try:
            strategy_response = self.strategy_class_obj.do_operation()
            LOGGER.add_metadata("strategy_response", strategy_response)
            LOGGER.info(f"Strategy response: {strategy_response}")
            return strategy_response
        except Exception as e:
            LOGGER.add_tempdata("error",str(e))
            LOGGER.error(f"Error in processing event from called strategy_class: {e}")
            return LambdaResponse.error(message=str(e))