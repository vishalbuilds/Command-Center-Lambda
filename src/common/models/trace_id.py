import uuid


TRACE_ID_CACHE = None


class TraceId:
    @staticmethod
    def init(context):
        global TRACE_ID_CACHE
        TRACE_ID_CACHE = (
            context["aws_request_id"]
            if context.get("aws_request_id", "")
            else str(uuid.uuid4())
        )

    @staticmethod
    def get():
        return TRACE_ID_CACHE

    @staticmethod
    def set(trace_id):
        global TRACE_ID_CACHE
        TRACE_ID_CACHE = trace_id
