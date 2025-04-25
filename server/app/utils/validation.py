from pydantic import EmailStr, ValidationError
from pydantic_core import PydanticCustomError

# Password validation
# Checks if password is long enough, contains uppercase and lowercase letters, and has a number
def validate_password(
    password: str,
) -> tuple[
    bool, list[str]
]:  # use typing.Tuple and typing.List for older version of Python
    # Returns Tuple: (is_valid: bool, errors: list[str]) - List is empty of no errors are found
    errors = []

    if len(password) < 6:
        errors.append("Password must contain 6 or more characters")
    if not any(c.isupper() for c in password):
        errors.append("Password must contain at least one uppercase letter")
    if not any(c.islower() for c in password):
        errors.append("Password must contain at least one lowercase letter")
    if not any(c.isdigit() for c in password):
        errors.append("Password must contain at least one number")

    return (len(errors) == 0, errors)


# Email Validation
def validate_email(email: str) -> tuple[bool, str]:
    try:
        EmailStr.validate(email)  # Checks email format and DNS MX record
        return True, ""
    except PydanticCustomError as e:
        return False, str(e)