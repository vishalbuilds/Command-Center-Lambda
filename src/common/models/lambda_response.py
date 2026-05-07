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
        json_string_flat: bool = False,
    ) -> Dict[str, Any]:
        if ts is None:
            ts = datetime.now(timezone.utc)

        if json_string_flat:
            return {
                **(data or {}),
                "result": result,
                "statusCode": str(status_code),
                "message": message or "",
                "timestamp": ts.isoformat(),
            }

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
        json_string_flat: bool = False,
    ) -> Dict[str, Any]:
        return LambdaResponse._build_response(
            status_code=status_code,
            result="success",
            message=message,
            data=data,
            ts=ts,
            json_string_flat=json_string_flat,
        )

    @staticmethod
    def error(
        message: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        ts: Optional[datetime] = None,
        status_code: int = 400,
        json_string_flat: bool = False,
    ) -> Dict[str, Any]:
        return LambdaResponse._build_response(
            status_code=status_code,
            result="error",
            message=message,
            data=data,
            ts=ts,
            json_string_flat=json_string_flat,
        )
