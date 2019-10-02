import pkg_resources as pkg
import inspect

# noinspection PyCompatibility
try:
    from pathlib import Path
except:
    from pathlib2 import Path


def filename_resolver(package=None):
    if package is None:
        caller_package = inspect.getmodule(inspect.stack()[1][0]).__name__
        package = caller_package

    resource_manager = pkg.ResourceManager()

    def func(resource):
        return resource_manager.resource_filename(package, resource)

    # noinspection PyCompatibility
    func.__doc__ = "Computes file names for resources located in {}".format(package)

    return func


def path_resolver(package=None):

    resolver = filename_resolver(package)

    def func(resource):
        filename = resolver(resource)
        return Path(filename)

    if package is None:
        package = "caller package"

    # noinspection PyCompatibility
    func.__doc__ = "Computes Path for resources located in {}".format(package)

    return func
