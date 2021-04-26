# define Python user-defined exceptions
class Error(Exception):
    """Base class for other exceptions"""
    pass


class CreatePoolManagerFailure(Error):
    """Raised when the input value is too small"""
    pass


class RequestError(Error):
    """Raised when the input value is too large"""
    pass

class HttpRequestError(Error):
    """Raised when the input value is too large"""
    pass
