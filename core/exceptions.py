'''
This module defines custom exceptions for the application.
'''

class AppException(Exception):
    '''Base class for all custom exceptions in the application.'''
    def __init__(self,detail:str):
        self.detail = detail
        super().__init__(detail)


#User Exceptions
      
class UserAlreadyExistsError(AppException):
    '''Exception raised when trying to create a user that already exists.'''
    pass

class UserNotFoundError(AppException):
    '''Exception raised when a user is not found.'''
    pass

class UserNotVerifiedError(AppException):
    '''Exception raised when a user is not verified.'''
    pass

class UserInactiveError(AppException):
    '''Exception raised when a user is inactive.'''
    pass

#Authentication Exceptions

class InvalidCredentialsError(AppException):
    '''Exception raised when the provided credentials are invalid.'''
    def __init__(self,detail:str="Invalid credentials provided."):
        super().__init__(detail)

class TokenExpiredError(AppException):
    '''Exception raised when an authentication token has expired.'''
    def __init__(self,detail:str="Authentication token has expired."):
        super().__init__(detail)

class InvalidTokenError(AppException):
    '''Exception raised when an authentication token is invalid.'''
    def __init__(self,detail:str="Invalid authentication token."):
        super().__init__(detail)

# OTP Exceptions

class InvalidOTPError(AppException):
    '''Exception raised when an invalid OTP is provided.'''
    def __init__(self,detail:str="Invalid OTP provided."):
        super().__init__(detail)

class OTPExpiredError(AppException):
    '''Exception raised when an OTP has expired.'''
    def __init__(self,detail:str="OTP has expired."):
        super().__init__(detail)

class OTPAlreadyUsedError(AppException):
    '''Exception raised when an OTP has already been used.'''
    def __init__(self,detail:str="OTP has already been used."):
        super().__init__(detail)


# session exceptions

class SessionNotFoundError(AppException):
    '''Exception raised when a session is not found.'''
    def __init__(self,detail:str="Session not found."):
        super().__init__(detail)

class SessionRevokedError(AppException):
    '''Exception raised when a session has been revoked.'''
    def __init__(self,detail:str="Session has been revoked."):
        super().__init__(detail)

