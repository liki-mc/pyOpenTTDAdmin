

class PyOpenTTDAdminError(Exception): pass

class AuthenticationError(PyOpenTTDAdminError, ValueError): pass

class UnknownAuthenticationError(AuthenticationError):
    def __init__(self, message: str, *args, **kwargs):
        message += "\nPlease make an issue on github: github.com/liki-mc/pyOpenTTDAdmin"
        super().__init__(message, *args, **kwargs)
