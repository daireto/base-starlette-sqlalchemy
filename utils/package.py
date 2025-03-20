"""This module provides the ``get_all_package_clases`` function
to get all the classes in a package and the ``set_classes``
function to set them to a module.
"""

import os
import sys


def get_all_package_clases(
    _file_: str,
    _name_: str,
    suffix: str = '',
    parent_class: type | None = None,
) -> list[type]:
    """Gets all the first level classes
    in a package.

    It must be called from the __init__.py file
    in the package folder.

    Usage:
    >>> get_all_package_clases(__file__, __name__)
    [Class1, Class2, ...]

    Search in files with the suffix ``_router.py``:
    >>> get_all_package_clases(__file__, __name__, '_middleware.py')
    [Middleware1, Middleware2, ...]

    Search subclasses of a class:
    >>> get_all_package_clases(__file__, __name__, parent_class=BaseRouter)
    [Router1, Router2, ...]

    Parameters
    ----------
    _file_ : str
        The ``__file__`` variable.
    _name_ : str
        The ``__name__`` variable.
    suffix : str, optional
        Suffix of the files in which
        to search for the classes.
    parent_class : type | None, optional
        Checks if the class is a subclass, by default None.

    Returns
    -------
    list[type]
        List of classes.

    Raises
    ------
    Exception
        If running the ``__init__.py`` file.
    ValueError
        - If this function is not called from
        the ``__init__.py`` file in the package folder.
        - If there are duplicated class names.
    """
    __file__ = _file_
    __name__ = _name_

    path = os.path.dirname(os.path.abspath(__file__))
    basename = os.path.basename(path)
    if __name__ == '__main__':
        raise RuntimeError(
            'this function will not work when running the __init__.py file'
        )

    if __name__ != basename:
        raise ValueError(
            f'this function must be called from the __init__.py file '
            f'in the {basename!r} folder'
        )

    class_list = []
    class_names = {}
    suffix = suffix[:-3] if suffix.endswith('.py') else suffix
    py_modules = [
        f[:-3]
        for f in os.listdir(path)
        if f.endswith(f'{suffix}.py') and f != '__init__.py'
    ]
    for py in py_modules:
        mod = __import__('.'.join([__name__, py]), fromlist=[py])
        classes = [
            getattr(mod, x)
            for x in dir(mod)
            if isinstance(getattr(mod, x), type)
        ]
        for cls in classes:
            if parent_class is not None and (
                cls == parent_class or not issubclass(cls, parent_class)
            ):
                continue

            if cls.__name__ in class_names:
                if class_names[cls.__name__] == id(cls):
                    continue

                raise ValueError(
                    f'duplicated class name {cls.__name__!r} in {__name__!r}'
                )

            class_names[cls.__name__] = id(cls)
            class_list.append(cls)

    return class_list


def set_classes(_name_: str, classes: list[type]) -> None:
    """Sets classes to a module.

    Parameters
    ----------
    _name_ : str
        The ``__name__`` variable.
    classes : list[type]
        List of classes.
    """
    __name__ = _name_
    for cls in classes:
        setattr(sys.modules[__name__], cls.__name__, cls)
