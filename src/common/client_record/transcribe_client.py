import boto3
from common.logger import Logger

class TranscribeClient:
    def __init__(self, region_name="us-east-1"):
        self.logger = Logger(__name__)
        self.transcribe = boto3.client('transcribe', region_name=region_name)


