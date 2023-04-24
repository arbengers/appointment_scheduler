# Error handler
class GeneralError(Exception):
    """
        This is for general error
    """

    def __init__(self, error, severity, status_code):
        self.error = error
        self.severity = severity
        self.status_code = status_code
