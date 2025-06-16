"""Custom exceptions for the Ramayanam API."""

class RamayanamAPIException(Exception):
    """Base exception for all API errors."""
    
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class KandaNotFoundError(RamayanamAPIException):
    """Raised when a requested Kanda is not found."""
    
    def __init__(self, kanda_number: int):
        message = f"Kanda '{kanda_number}' not found"
        super().__init__(message, 404)

class SargaNotFoundError(RamayanamAPIException):
    """Raised when a requested Sarga is not found."""
    
    def __init__(self, sarga_number: int, kanda_number: int):
        message = f"Sarga '{sarga_number}' not found for Kanda '{kanda_number}'"
        super().__init__(message, 404)

class SlokaNotFoundError(RamayanamAPIException):
    """Raised when a requested Sloka is not found."""
    
    def __init__(self, sloka_number: int, sarga_number: int, kanda_number: int):
        message = f"Sloka '{sloka_number}' not found for Sarga '{sarga_number}' in Kanda '{kanda_number}'"
        super().__init__(message, 404)

class SearchError(RamayanamAPIException):
    """Raised when search operations fail."""
    
    def __init__(self, message: str = "Search operation failed"):
        super().__init__(message, 500)