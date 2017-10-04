class Owner(object):
    __slots__ = (
        'id', 'email', 'token'
    )

    def __init__(self, id, email, token=None):
        self.id = id
        self.email = email
        self.token = token
