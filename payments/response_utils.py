from rest_framework.response import Response
from rest_framework import status

def success(data=None):
    """
    Returns a success response.
    """
    return Response({"status": "success", "data": data}, status=status.HTTP_200_OK)

def created(data=None):
    """
    Returns a created response.
    """
    return Response({"status": "created", "data": data}, status=status.HTTP_201_CREATED)

def bad_request(data=None):
    """
    Returns a bad request response.
    """
    return Response({"status": "error", "data": data}, status=status.HTTP_400_BAD_REQUEST)

def not_found(data=None):
    """
    Returns a not found response.
    """
    return Response({"status": "error", "data": data}, status=status.HTTP_404_NOT_FOUND)

def forbidden(data=None):
    """
    Returns a forbidden response.
    """
    return Response({"status": "error", "data": data}, status=status.HTTP_403_FORBIDDEN)

def server_error(data=None):
    """
    Returns a server error response.
    """
    return Response({"status": "error", "data": data}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
