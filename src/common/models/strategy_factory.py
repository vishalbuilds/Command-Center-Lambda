from common.models.logger import Logger
from common.models.lambda_response import LambdaResponse
from workflow.amazon_connect.imports import *
from workflow.api_gateway_http.imports import *
from workflow.api_gateway_rest.imports import *
from workflow.functional_url.imports import *
from workflow.s3.imports import *


LOGGER = Logger(__name__)


class StrategyFactory:
    def __init__(self, event:dict, invoke_type: str):
        self.event = event
        self.invoke_type=invoke_type

        if not self._validate_strategy:
            LOGGER.error(f"Failed in process strategy")
            raise Exception(f"Failed in process strategy")
            
        self.strategy_class=self._initiate_strategy()


    #validation
    def _validate_strategy(self):
        if self.invoke_type not in globals():
            LOGGER.add_tempdata(f"Invalid invoke strategy type: {self.invoke_type}.")
            return False
        if "request_type" not in self.event:
            LOGGER.add_tempdata("Event must contain 'request_type")
            return False
        if self.event.get("request_type") not in globals().get(self.invoke_type):
            LOGGER.add_tempdata(f"Invalid strategy: {self.event.get('request_type')}")
            return False
        return True
            
    # #initiating the strategy and call the invocation class 
    # def _initiate_strategy(self, strategy_name):

                

    #         # try attribute variants: original, camelized
    #         attr_names = [str(strategy_name), snake_to_camel(mod_name)]
    #         for attr in attr_names:
    #             if hasattr(mod, attr):
    #                 strategy_class = getattr(mod, attr)
    #                 break
    #         if strategy_class:
    #             break

    #     if strategy_class is None:
    #         raise Exception(f"Strategy class '{strategy_name}' not found")

    #     # Instantiate strategy; many strategies accept event in constructor
    #     try:
    #         self._strategy = strategy_class(self.event)
    #     except TypeError:
    #         # Fallback to no-arg constructor
    #         self._strategy = strategy_class()
    #     LOGGER.info(f'Initialized strategy: {strategy_name}')   

    def execute(self):
        try:
            if not self.strategy_class.do_validate(self.event):
                LOGGER.add_tempdata("validation failed from called strategy_class")
                raise Exception("validation failed from called strategy_class")
        except Exception as e:
                LOGGER.add_tempdata("error",str(e))
                LOGGER.error(f"Error in validation from called strategy_class: {e}")
                return LambdaResponse.error(message=str(e))
        
        try:
            strategy_response = self.strategy_class(self.event)
            LOGGER.add_metadata("strategy_response", strategy_response)
            LOGGER.info(f"Strategy response: {strategy_response}")
            return strategy_response
        except Exception as e:
            LOGGER.add_tempdata("error",str(e))
            LOGGER.error(f"Error in processing event from called strategy_class: {e}")
            return LambdaResponse.error(message=str(e))