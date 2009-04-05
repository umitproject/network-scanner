class FileMissingError(Exception):
    def __init__(self, filename):
        self.filename = filename

    def __str__(self):
        return "File %r is missing." % self.filename

class OriginError(FileMissingError):
    def __init__(self, filename):
        super(OriginError, self).__init__(filename)

class DestinationError(FileMissingError):
    def __init__(self, filename):
        super(DestinationError, self).__init__(filename)
