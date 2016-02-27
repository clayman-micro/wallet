
class ImproperlyConfigure(Exception):
    pass


class Error(Exception):
    def __init__(self, errors):
        self.errors = errors


class DatabaseError(Error):
    pass


class ValidationError(Error):
    pass


class SerializationError(Error):
    pass


class ResourceNotFound(Exception):
    pass


class MultipleResourcesFound(Exception):
    pass