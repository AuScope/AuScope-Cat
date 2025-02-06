from io import IOBase
import json

def make_mock_session_fn(inp: str, code: int = 200):
    ''' Make a mock requests.Session.get() or post() function

    :param inp: string or file object containing the desired response
    :param code: HTTP return code, default 200
    :return: new mock Session.get() function returning a Response object
    '''
    # If it is a file obj or some i/o object
    if isinstance(inp, IOBase):
        resp_str = inp.read().rstrip('\n')
    else:
        resp_str = inp

    # If it is parseable JSON then return this also
    try:
        json_obj = json.loads(resp_str)
    except (TypeError, json.JSONDecodeError, UnicodeDecodeError) as e:
        json_obj = {}

    # This is what our function will return
    class MockFnResponse:
        text = resp_str
        status_code = code
        @staticmethod
        def json():
            return json_obj

    # Create our function
    def mock_fn(*args, **kwargs):
        return MockFnResponse()

    # Return mock function
    return mock_fn
