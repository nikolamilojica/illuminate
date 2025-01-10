class TestANSIException(Exception):
    """
    Test Exception with ANSI tag look
    a like message.
    """

    message = "\n<string>\n"

    def __init__(self, message=None):
        super().__init__(message or self.message)
