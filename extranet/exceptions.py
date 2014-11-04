class ConnectionError(Exception):
    """
    Impossible to establish a connection to the server
    """

class FatalError(Exception):
    """
    An unexpected error occured
    """

class LoginError(Exception):
    """
    Login failed
    """

