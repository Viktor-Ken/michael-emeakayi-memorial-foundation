import datetime

NAME_MAX = 100
EMAIL_MAX = 200
SUBJECT_MAX = 200
MESSAGE_MAX = 5000
ROLE_MAX = 100
BIO_MAX = 1000
TITLE_MAX = 200
LOCATION_MAX = 200
DESCRIPTION_MAX = 2000


def validate_contact(name, email, subject, message):
    if not name or not email or not message:
        return "Please fill in your name, email and message."
    if len(name) > NAME_MAX:
        return f"Your name is too long (maximum {NAME_MAX} characters)."
    if len(email) > EMAIL_MAX:
        return f"Your email address is too long (maximum {EMAIL_MAX} characters)."
    if len(subject) > SUBJECT_MAX:
        return f"The subject is too long (maximum {SUBJECT_MAX} characters)."
    if len(message) > MESSAGE_MAX:
        return f"Your message is too long (maximum {MESSAGE_MAX} characters)."
    if "@" not in email or " " in email or email.startswith("@") or email.endswith("@"):
        return "Please enter a valid email address."
    return None


def validate_trustee(name, role, bio):
    if not name or not role:
        return "Name and role are required."
    if len(name) > NAME_MAX:
        return f"The name is too long (maximum {NAME_MAX} characters)."
    if len(role) > ROLE_MAX:
        return f"The role is too long (maximum {ROLE_MAX} characters)."
    if len(bio) > BIO_MAX:
        return f"The bio is too long (maximum {BIO_MAX} characters)."
    return None


def validate_event(title, date, location, description):
    if not title or not date:
        return "Title and date are required."
    if len(title) > TITLE_MAX:
        return f"The title is too long (maximum {TITLE_MAX} characters)."
    if len(location) > LOCATION_MAX:
        return f"The location is too long (maximum {LOCATION_MAX} characters)."
    if len(description) > DESCRIPTION_MAX:
        return f"The description is too long (maximum {DESCRIPTION_MAX} characters)."
    try:
        datetime.date.fromisoformat(date)
    except ValueError:
        return "Please use a valid date in YYYY-MM-DD format."
    return None
