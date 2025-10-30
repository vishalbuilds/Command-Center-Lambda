from strategies.workflow.s3_remove_pii import S3RemovePii
from strategies.workflow.s3_get_file import S3GetFile
from strategies.workflow.status_checker import StatusChecker 
from common.logger import Logger

LOGGER = Logger(__name__)

VALID_FACTORY_STRATEGIES = [
    's3_remove_pii',
    'S3GetFile',
    'StatusChecker'
]

class StrategyFactory:
    def __init__(self, event):
        self.event = event
        if "request_type" not in self.event:
            raise Exception("Event must contain 'request_type'")
        if not self._validate_strategy():
            raise Exception(f"Invalid strategy: {self.event.get('request_type')}")
        self._initiate_strategy(self.event.get("request_type"))

    def _validate_strategy(self):
        strategy_name = self.event.get("request_type")
        if strategy_name in VALID_FACTORY_STRATEGIES:
            LOGGER.info(f'Valid strategy {strategy_name} found')
            return True
        LOGGER.warning(f'Invalid strategy {strategy_name}')
        return False

    def _initiate_strategy(self, strategy_name):
        strategy_class = globals().get(strategy_name)
        if strategy_class is None:
            raise Exception(f"Strategy class '{strategy_name}' not found")
        self._strategy = strategy_class(self.event)
        LOGGER.info(f'Initialized strategy: {strategy_name}')   

    def execute(self):
        return self._strategy.handle(self.event)
