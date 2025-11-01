"""
AWS Lambda Invocation Source Detector

A utility to identify common Lambda invocation sources:
- Amazon Connect
- API Gateway (REST API v1)
- API Gateway (HTTP API v2)
- Lambda Function URL
- S3 Events
- EventBridge/CloudWatch Events
- Direct Invoke
"""
from typing import Literal

InvocationSource = Literal[
    "AMAZON_CONNECT",
    "API_GATEWAY_REST",
    "API_GATEWAY_HTTP",
    "FUNCTION_URL",
    "S3",
    "EVENTBRIDGE",
    "DIRECT_INVOKE"
]

def _is_amazon_connect(event: dict) -> bool:
    """Check if the event is from Amazon Connect."""
    
    if "Details" in event and "ContactData" in event.get("Details", {}):
        return True
   
    if "Name" in event and isinstance(event.get("Name"), str):
        name_lower = event["Name"].lower()
        return "contact" in name_lower or "connect" in name_lower
    return False

def _is_s3_event(event: dict) -> bool:
    """Check if the event is from S3."""
    if "Records" not in event:
        return False
    
    # Check first record for S3 event source
    if event["Records"]:
        first_record = event["Records"][0]
        event_source = first_record.get("eventSource") or first_record.get("EventSource")
        return event_source == "aws:s3"
    
    return False

def _is_eventbridge(event: dict) -> bool:
    """Check if the event is from EventBridge/CloudWatch Events."""
    # EventBridge events have both 'detail-type' and 'source' fields
    # But make sure it's not an S3 event (which can also have 'source')
    return "detail-type" in event and "source" in event and "Records" not in event

def _is_function_url(request_context: dict) -> bool:
    """Check if the event is from a Lambda Function URL."""
    domain_name = request_context.get("domainName", "")
    return ".lambda-url." in domain_name

def _is_api_gateway_http(request_context: dict) -> bool:
    """Check if the event is from API Gateway v2 (HTTP API)."""
    return "http" in request_context

def _is_api_gateway_rest(request_context: dict) -> bool:
    """Check if the event is from API Gateway v1 (REST API)."""
    
    return ("apiId" in request_context or "stage" in request_context) and \
           not _is_function_url(request_context)

def get_invocation_source(event: dict) -> InvocationSource:
    """
    Detect the source of a Lambda invocation from the event structure.
    
    Args:
        event: The Lambda event dictionary
        
    Returns:
        A string identifier for the invocation source
        
    Examples:
        >>> event = {"Details": {"ContactData": {}}, "Name": "ContactFlowEvent"}
        >>> get_invocation_source(event)
        'AMAZON_CONNECT'
        
        >>> event = {"headers": {}, "requestContext": {"apiId": "abc123"}}
        >>> get_invocation_source(event)
        'API_GATEWAY_REST'
        
        >>> event = {"Records": [{"eventSource": "aws:s3", "s3": {...}}]}
        >>> get_invocation_source(event)
        'S3'
    """
    
    if _is_amazon_connect(event):
        return "AMAZON_CONNECT"
    
    if _is_s3_event(event):
        return "S3"
    
    if _is_eventbridge(event):
        return "EVENTBRIDGE"

    if "headers" in event and "requestContext" in event:
        request_context = event["requestContext"]
        
        if _is_function_url(request_context):
            return "FUNCTION_URL"
        if _is_api_gateway_http(request_context):
            return "API_GATEWAY_HTTP"
        if _is_api_gateway_rest(request_context):
            return "API_GATEWAY_REST"
    
    return "DIRECT_INVOKE"

def extract_event_data(event: dict, invocation_source: InvocationSource) -> dict:
    """
    Extract the main data section from the event based on invocation source.
    Returns the relevant sub-dictionary that contains the actual data.
    
    Args:
        event: The Lambda event dictionary
        invocation_source: The type of invocation source
        
    Returns:
        The relevant data section from the event
        
    Examples:
        >>> # For Amazon Connect, returns ContactData
        >>> data = extract_event_data(event, "AMAZON_CONNECT")
        >>> print(data['ContactId'])
        
        >>> # For API Gateway, returns requestContext
        >>> data = extract_event_data(event, "API_GATEWAY_REST")
        >>> print(data['apiId'])
        
        >>> # For S3, returns the Records array
        >>> data = extract_event_data(event, "S3")
        >>> print(data[0]['s3']['bucket']['name'])
    """
    if invocation_source == "AMAZON_CONNECT":
        return event.get("Details", {}).get("ContactData", {})
    elif invocation_source in ("API_GATEWAY_REST", "API_GATEWAY_HTTP", "FUNCTION_URL"):
        return event.get("requestContext", {})
    elif invocation_source == "S3":
        return event.get("Records", [])
    elif invocation_source == "EVENTBRIDGE":
        return event.get("detail", {})
    else:  # DIRECT_INVOKE
        return event