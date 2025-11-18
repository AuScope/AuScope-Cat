from .auscopecatQGIS import AuscopecatPlugin


def classFactory(iface):
    return AuscopecatPlugin(iface)
