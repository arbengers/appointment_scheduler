# Error handler
class InvalidBodyError(Exception):
    """
        This is for invalid body error
    """

    def __init__(self, error):
        self.error = error
        self.severity = 'info'
        self.status_code = 400
