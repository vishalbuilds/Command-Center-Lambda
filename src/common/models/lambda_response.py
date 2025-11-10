import json
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Literal


class LambdaResponse:

    @staticmethod
    def _build_response(
        result: Literal["success", "error"],
        message: Optional[str],
        status_code: int,
        data: Optional[Dict[str, Any]],
        ts: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        if ts is None:
            ts = datetime.now(timezone.utc)

        return {
            "statusCode": status_code,
            "result": result,
            "body": json.dumps(
                {
                    "message": message,
                    "data": data,
                    "timestamp": ts.isoformat(),
                }
            ),
        }

    @staticmethod
    def success(
        message: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        ts: Optional[datetime] = None,
        status_code: int = 200,
    ) -> Dict[str, Any]:
        return LambdaResponse._build_response(
            status_code=status_code, result="success", message=message, data=data, ts=ts
        )

    @staticmethod
    def error(
        message: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        ts: Optional[datetime] = None,
        status_code: int = 400,
    ) -> Dict[str, Any]:
        return LambdaResponse._build_response(
            status_code=status_code, result="error", message=message, data=data, ts=ts
        )
