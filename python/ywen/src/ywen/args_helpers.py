import functools


DEPRECATION_TAG = "[DEPRECATED]"


def arg_help(
    help: str,
    default_value: str=None,
    deprecated: bool=False,
) -> str:
    """Return the help message with the default value (if provided) and the
    deprecation warning (if needed).
    """

    default_value_part = (
        f" (default: {default_value})" if default_value is not None else ""
    )
    deprecation_warning = f"{DEPRECATION_TAG} " if deprecated else ""

    return f"{deprecation_warning}{help}{default_value_part}"


# NOTE(ywen): Since we released the function signature and the consuming code
# has been passing in the parameter called `default`, we need to maintain the
# backward-compatibility to make sure the function still expose the parameter
# `default`. But using `functools.partial` over `arg_help` will change
# `default` to `default_value`, so we need to wrap `arg_help`.
def arg_help_with_default(
    help: str,
    default: str,
) -> str:
    return arg_help(help=help, default_value=default)


arg_help_with_deprecation_warning = functools.partial(
    arg_help, default_value=None, deprecated=True,
)
