import enum


class APPErrorTypes(enum.Enum):
    VALIDATION_ERROR = (4001, "validation error")
    DUPLICATION_ERROR = (4002, "duplication error")
    CREDENTIALS_ERROR = (4040, "invalid credentials")
    USER_BLOCKED = (4041, "user blocked")
    USER_UN_BLOCKED = (4041, "user un-blocked")
    USER_DEACTIVATED = (4042, "user deactivated")
    USER_ACTIVATED = (4043, "user activated")
    ACCOUNT_NOT_VERIFIED = (4044, "account not verified")
    USER_NOT_FOUND = (4045, "user not found")
    UNAUTHORIZED_ACCESS = (4046, "user is not authenticated")
    FORBIDDEN_RESOURCE_ACCESS = (4047, "forbidden resource")
    RESOURCE_NOT_FOUND = (4048, "resource not found")
    INVALID_CREDENTIALS = (4049, "invalid credentials")
    BAD_REQUEST = (4050, "bad request")
    EMAIL_LINK_INVALID = (4051, "invalid verification link")
    REFRESH_TOKEN_REQUIRED = (4052, "refresh token required")
    TOKEN_REFRESH_FAILED = (4052, "failed to created access token")
    UNHANDLED_ERROR = (4053, "unhandled error")

    INVALID_FILE_TYPE = (4060, "invalid file type")

    OPERATION_NOT_ALLOWED = (4070, "operation not allowed")

    CONFLICT = (4075, "conflict")

    API_NOT_FOUND = (4080, "API not found")
    INTERNAL_SERVER_ERROR = (5001, "internal server error")
