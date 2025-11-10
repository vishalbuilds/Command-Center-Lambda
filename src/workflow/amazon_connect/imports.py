from workflow.amazon_connect.status_checker_connect import StatusCheckerConnect
from workflow.amazon_connect.auto_clean_up_active_contacts import (
    AutoCleanUpActiveContacts,
)
from workflow.amazon_connect.phone_number_format import PhoneNumberFormat
from workflow.amazon_connect.dynamodb_lookup import DynamodbLookup
from workflow.amazon_connect.dynamodb_lookup_check import DynamoDBLookupCheck
from workflow.amazon_connect.dynamodb_store_attributes import DynamoDBStoreAttributes


# invocation source class
AMAZON_CONNECT = [
    "StatusCheckerConnect",
    "AutoCleanUpActiveContacts",
    "PhoneNumberFormat",
    "DynamodbLookup",
    "DynamoDBLookupCheck",
    "DynamoDBStoreAttributes",
]
