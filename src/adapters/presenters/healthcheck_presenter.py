from src.shared.responses import error_response, success_response


def present_healthcheck(result: dict):
    if result["database"].get("status") == "OK":
        return success_response(
            code="HEALTHCHECK_OK",
            message="Service is healthy",
            data=result
        )
    else:
        return error_response(
            code="HEALTHCHECK_FAIL",
            message="Database connection failed",
            data=None
        )
