class AccessTokenInvalidError(Exception):
    message = "Access token is invalid."

    def __init__(self, message=None):
        self.message = message or self.message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class RefreshTokenInvalidError(Exception):
    message = "Refresh token is invalid."

    def __init__(self, message=None):
        self.message = message or self.message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class ClassInstanceMissmatchError(Exception):
    message = "Variable is not instance of given class"

    def __str__(self):
        return ClassInstanceMissmatchError.message


class EntityNotFoundException(Exception):
    message = "Entity not found in database"

    def __init__(self, message=None):
        self.message = message or self.message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class PasswordValidationError(Exception):
    message = "Password must be 8 to 100 characters long and include one number, one symbol,  one uppercase letter " \
              "and one lowercase letter"

    def __init__(self, message=None):
        self.message = message or self.message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class UserPermissionDeniedError(Exception):
    message = "User has no permission for given operation"

    def __init__(self, message=None):
        self.message = message or self.message
        super().__init__(self.message)

    def __str__(self):
        return self.message
