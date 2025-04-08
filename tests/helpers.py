from io import IOBase
import json
import pandas as pd
import numpy as np

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
    except (TypeError, json.JSONDecodeError, UnicodeDecodeError):
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


def get_all_csv_df() -> pd.DataFrame:
    """ Returns a DataFrame of the first few rows of https://nvclstore.z8.web.core.windows.net/all.csv
    """
    all_csv_dict = {'State': {0: 'NT', 1: 'NT', 2: 'NT', 3: 'NT'},
 'DatasetName': {0: '8440735_11CPD005', 1: '8418381_BND1', 2: '8434796_YG35RD', 3: '8471153_CCD09'},
 'BoreholeName': {0: '11CPD005', 1: 'BND1', 2: 'YG35RD', 3: 'CCD09'},
 'BoreholeURI': {0: 'http://geology.data.nt.gov.au/resource/feature/ntgs/borehole/8440735_11CPD005',
  1: 'http://geology.data.nt.gov.au/resource/feature/ntgs/borehole/8418381_BND1',
  2: 'http://geology.data.nt.gov.au/resource/feature/ntgs/borehole/8434796_YG35RD',
  3: 'http://geology.data.nt.gov.au/resource/feature/ntgs/borehole/8471153_CCD09'},
 'Latitude': {0: -23.76822, 1: -17.54575433, 2: -22.668285, 3: -15.96675475},
 'Longitude': {0: 136.85487, 1: 136.89385355, 2: 131.937275, 3: 135.53679738},
 'StartDepth': {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0},
 'EndDepth': {0: 652.3, 1: 140.83, 2: 241.3, 3: 252.5},
 'FileModifiedDate': {0: '23/06/2022',
  1: '23/06/2022',
  2: '23/06/2022',
  3: '23/06/2022'},
 'DownloadLink': {0: 'https://nvclstore.data.auscope.org.au/NT/8440735_11CPD005.zip',
  1: 'https://nvclstore.data.auscope.org.au/NT/8418381_BND1.zip',
  2: 'https://nvclstore.data.auscope.org.au/NT/8434796_YG35RD.zip',
  3: 'https://nvclstore.data.auscope.org.au/NT/8471153_CCD09.zip'},
 'Has VSWIR': {0: True, 1: True, 2: True, 3: True},
 'Has MIR': {0: False, 1: False, 2: False, 3: False},
 'Has TIR': {0: True, 1: False, 2: True, 3: True},
 'Has Vis System TSA': {0: True, 1: True, 2: True, 3: True},
 'Vis System TSA Version': {0: 704.0, 1: 601.0, 2: 704.0, 3: 704.0},
 'Has SWIR System TSA': {0: True, 1: True, 2: True, 3: True},
 'SWIR System TSA Version': {0: 705.0, 1: 631.0, 2: 705.0, 3: 705.0},
 'Has TIR System TSA': {0: False, 1: False, 2: False, 3: False},
 'TIR System TSA Version': {0: np.nan, 1: np.nan, 2: np.nan, 3: np.nan},
 'Has Vis User TSA': {0: True, 1: True, 2: True, 3: True},
 'Vis User TSA Version': {0: 704.0, 1: 601.0, 2: 704.0, 3: 704.0},
 'Has SWIR User TSA': {0: False, 1: True, 2: True, 3: False},
 'SWIR User TSA Version': {0: np.nan, 1: 700.0, 2: 705.0, 3: np.nan},
 'Has TIR User TSA': {0: False, 1: False, 2: True, 3: False},
 'TIR User TSA Version': {0: np.nan, 1: np.nan, 2: 707.0, 3: np.nan},
 'Has System JCLST': {0: True, 1: False, 2: True, 3: True},
 'JCLST System Version': {0: 707.0, 1: np.nan, 2: 706.0, 3: 707.0},
 'Has User JCLST': {0: False, 1: False, 2: False, 3: False},
 'JCLST User Version': {0: np.nan, 1: np.nan, 2: np.nan, 3: np.nan},
 'Tray Count': {0: 97.0, 1: 15.0, 2: 11.0, 3: 62.0},
 'Source last Modified': {0: '11/12/2024',
  1: '11/12/2024',
  2: '11/12/2024',
  3: '11/12/2024'}}
    return pd.DataFrame(all_csv_dict)
