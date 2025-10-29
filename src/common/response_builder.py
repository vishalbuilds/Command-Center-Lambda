import json
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Literal


class ResponseBuilder:
    def _build_response(
        self,
        status_code: int,
        result: Literal['success', 'error'],
        message: Optional[str],
        data: Optional[Dict[str, Any]],
        ts: Optional[datetime]
    ) -> Dict[str, Any]:
        if ts is None:
            ts = datetime.now(timezone.utc)

        return {
            "statusCode": status_code,
            "result": result,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "message": message,
                "data": data,
                "timestamp": ts.isoformat(),
            }),
        }

    def success(
        self,
        status_code: int = 200,
        message: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        ts: Optional[datetime] = None
    ) -> Dict[str, Any]:
        return self._build_response(
            status_code=status_code,
            result='success',
            message=message,
            data=data,
            ts=ts
        )

    def error(
        self,
        status_code: int = 400,
        message: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        ts: Optional[datetime] = None
    ) -> Dict[str, Any]:
        return self._build_response(
            status_code=status_code,
            result='error',
            message=message,
            data=data,
            ts=ts
        )
