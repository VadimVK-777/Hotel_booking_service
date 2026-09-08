"""JSON error responses for failures outside DRF views."""

from django.http import HttpRequest, JsonResponse


def json_not_found(
    _request: HttpRequest,
    exception: Exception | None = None,
) -> JsonResponse:
    del exception
    return JsonResponse({"error": "Not found"}, status=404)


def json_server_error(_request: HttpRequest) -> JsonResponse:
    return JsonResponse({"error": "Internal server error"}, status=500)
