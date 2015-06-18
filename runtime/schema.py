""" Module designed to help ensure structured data is structured in a particular manner.
By using the schema decorator and passing a dictionary of keys and types as the annotation,
it validates that the given argument matches the structure of the annotation.

If an annotation is not a dictionary or iterable, it simply ignores it, allowing composition
with asserts.py's typecheck decorator."""

import functools
from collections import Iterable


def schema(function):
    """Check that a function's arguments match the given schemas."""

    @functools.wraps(function)
    def validated_function(*args, **kwargs):
        for i, arg in enumerate(args[:function.__code__.co_nlocals]):
            _validate_schema(function, function.__code__.co_varnames[i], arg)
        for name, arg in kwargs.items():
            _validate_schema(function, name, arg)

        result = function(*args, **kwargs)

        _validate_schema(function, 'return', result)
        return result

    return validated_function


def _validate_schema(f, name, arg):
    ann_schema = f.__annotations__.get(name, None)
    if ann_schema is not None:
        _format_asserts(ann_schema, arg)


def _format_asserts(form, data):
    """Checks that for each key value pair in form,
    there is a matching one in data where the value is the type
    specified in form."""
    try:
        form_items = form.items()
    except AttributeError:
        if not isinstance(form, Iterable):
            # in this case, do nothing.
            form_items = []
        else:
            form_items = form

    print("current form_items: {}".format(form_items))
    for key, value in form_items:
        if key not in data:
            try:
                assert isinstance(None, value)
            except TypeError:
                assert isinstance(None, type(value))
        elif isinstance(value, dict):
            assert isinstance(data[key], dict)
            _format_asserts(value, data[key])
        elif isinstance(value, list):
            assert isinstance(data[key], list)
            for item in value:
                assert isinstance(item, form[key][0])
        else:
            assert key in data
            assert isinstance(data[key], value)

    return data
