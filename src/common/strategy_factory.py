from common.models.logger import Logger
import re
import importlib

LOGGER = Logger(__name__)

VALID_CONNECT_STRATEGIES = [
    's3_remove_pii',
    'S3GetFile',
    'StatusChecker'
]

VALID_AG_STRATEGIES = []
VALID_EB_CW_STRATEGIES = []
VALID_URL_STRATEGIES = []
VALID_OTHER_STRATEGIES = []
VALID_DIRECT_INVOKE_STRATEGIES = []



class StrategyFactory:
    def __init__(self, event, invoke_type: str):
        self.event = event
        self.invoke_type=invoke_type
        if "request_type" not in self.event:
            LOGGER.error("Event must contain 'request_type'")
            raise Exception("Event must contain 'request_type'")
            
        
        if not self._validate_strategy():
            raise Exception(f"Invalid strategy: {self.event.get('request_type')}")
        self._initiate_strategy(self.event.get("request_type"))

    def _validate_strategy(self):
        if self.event.get("request_type","")
        LOGGER.warning(f'Invalid strategy {strategy_name}')
        return False

    def _initiate_strategy(self, strategy_name):
        # Dynamically import the workflow module that should contain the strategy class.
        # Build candidate module names from the strategy_name.
        def camel_to_snake(name: str) -> str:
            s1 = re.sub('(.)([A-Z][a-z]+)', r"\1_\2", name)
            return re.sub('([a-z0-9])([A-Z])', r"\1_\2", s1).lower()

        def snake_to_camel(name: str) -> str:
            return ''.join(part.capitalize() for part in name.split('_'))

        candidates = []
        raw = str(strategy_name)
        candidates.append(raw.lower())
        candidates.append(camel_to_snake(raw))
        # dedupe
        candidates = list(dict.fromkeys(candidates))

        strategy_class = None
        last_exc = None
        for mod_name in candidates:
            full_mod = f"workflow.{mod_name}"
            try:
                mod = importlib.import_module(full_mod)
            except Exception as e:
                last_exc = e
                continue

            # try attribute variants: original, camelized
            attr_names = [str(strategy_name), snake_to_camel(mod_name)]
            for attr in attr_names:
                if hasattr(mod, attr):
                    strategy_class = getattr(mod, attr)
                    break
            if strategy_class:
                break

        if strategy_class is None:
            raise Exception(f"Strategy class '{strategy_name}' not found")

        # Instantiate strategy; many strategies accept event in constructor
        try:
            self._strategy = strategy_class(self.event)
        except TypeError:
            # Fallback to no-arg constructor
            self._strategy = strategy_class()
        LOGGER.info(f'Initialized strategy: {strategy_name}')   

    def execute(self):
        # Call strategy.handle with the event only (tests expect single-arg calls)
        return self._strategy.handle(self.event)
