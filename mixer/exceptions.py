class WebException(Exception):
    """Web request returns unsucessful status."""

    def __init__(self, status, text, msg = None):
        self.status = status
        self.text = text
        msg = msg or "Got status code other than 200."
        super().__init__(msg)

class NotFound(WebException):
    """Web request returned 404 status code."""

    def __init__(self, text):
        msg = "Got status code 404."
        super().__init__(404, text, msg)
