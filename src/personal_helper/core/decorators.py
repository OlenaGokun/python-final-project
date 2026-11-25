import functools
from .exceptions import CommandError
from .formatting import error_message


def input_error(func):
    """Handle command errors with user-friendly messages and hints"""

    @functools.wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except CommandError as e:
            # CommandError and all subclasses have user-friendly messages
            # Includes all domain and input validation errors
            return error_message(f"❌ {str(e)}")
        except Exception as e:
            # Unexpected error - should not happen in normal operation
            return error_message(f"⚠️ Unexpected error: {e}")

    return inner
