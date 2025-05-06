from email_validator import validate_email as check_email, EmailNotValidError

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
        # Check format and optionally, the domain with (check_deliverability=True)
        valid = check_email(email, check_deliverability=True)
        return True, ""
    except EmailNotValidError as e:
        return False, str(e)