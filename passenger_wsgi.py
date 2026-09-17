from a2wsgi import ASGIMiddleware

from main import MAIN


# Passenger and other WSGI servers commonly look for a module-level
# ``application`` callable. a2wsgi adapts the FastAPI ASGI app to WSGI.
application = ASGIMiddleware(MAIN)

# Compatibility alias for hosting configurations that reference APPLICATION.
APPLICATION = application
