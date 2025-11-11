import uuid


TRACE_ID_CACHE = None


class TraceId:
    @staticmethod
    def init(context):
        global TRACE_ID_CACHE
        
        # Handle both dict (for tests) and object (for real Lambda context)
        if isinstance(context, dict):
            aws_request_id = context.get("aws_request_id", "")
        else:
            aws_request_id = getattr(context, "aws_request_id", None)
        
        TRACE_ID_CACHE = aws_request_id if aws_request_id else str(uuid.uuid4())

    @staticmethod
    def get():
        return TRACE_ID_CACHE

    @staticmethod
    def set(trace_id):
        global TRACE_ID_CACHE
        TRACE_ID_CACHE = trace_id
