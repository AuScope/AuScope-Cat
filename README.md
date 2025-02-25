![Test Status](https://github.com/AuScope/AuScope-Cat/actions/workflows/python-build-test.yml/badge.svg)

# AuScope Catalogue
Home of 'auscopecat', a Python package that aims to allow access to AuScope's catalogue of geoscience datasets from sources all over Australia

## Development

### To install

1. Install Python v3.10 or higher (https://www.python.org/)
2. Install uv (https://docs.astral.sh/uv/getting-started/installation/)
3. Clone this repository

### To create and activate a new Python environment

```
$ uv venv
$ uv sync
$ source .venv/bin/activate
```

And to deactivate:
```
$ deactivate
```

**ALSO**

```
uv run $SHELL
```
will run an environment in a new shell

### To search for WFS borehole datasets and download from one of them

```
$ uv run $SHELL
$ python3
>>> from auscopecat.api import search, download
>>> from auscopecat.auscopecat_types import ServiceType, DownloadType
>>> first_wfs = search('borehole', ServiceType.WFS)[0]
>>> BBOX = {
... "north": -24.7257367141281, "east": 131.38891993801204,
...  "south": -25.793715746583374, "west": 129.77844446004175
... }
>>> download(first_wfs, DownloadType.CSV, bbox=BBOX)
```

### To run tests

Run
```
uv run pytest
```
in the 'AuScope-Cat'root directory


