def singleton(cls):
    """
    A decorator that converts a class into a singleton.
    A typical example usage is:
        @singleton
        class MyClass:
            ...

    Args:
        cls: The class to be converted into a singleton.

    Returns:
        The singleton instance of the class.
    """
    instances = {}

    def wrapper(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return wrapper
