from functools import lru_cache
from uuid import uuid4


# create an in-memory cache for sessions to be looked up by the ID
# we will store in the browser cookie via FastHTML's session object.
# put a max of 100 active sessions to avoid unbounded memory usage.
@lru_cache(maxsize=100)
def get_session_by_id(id):
    session = dict()
    session.setdefault("stac_format_d", {})
    session.setdefault("form_format_d", {})
    session["form_format_d"].setdefault("assets", {})
    return session


def load_session(fasthtml_session):
    session_id = fasthtml_session.setdefault("session_id", str(uuid4()))
    return get_session_by_id(session_id)
