class StatusCheckerAPIGateWayRest:
    def __init__(self, event):
        self.event = event

    def do_validate(self):
        return (True, None)

    def do_operation(self):
        """
        Handle status check request for API Gateway REST.
        """
        return {
            "statusCode": 200,
            "message": "Status check successful",
            "service": "api_gateway_rest",
            "status": "healthy",
            "event": self.event,
        }
