class StatusChecker:
    def __init__(self,event):
        self.event = event
        

    def _check_status(self,event):
        return {
            'event': event.get('call'),
            'key': event.get('input').get('key'),
            'status': 'OK',
            'message': 'Lambda function is up and running'
        }
    def handle(self, event):
        return self._check_status(event)
