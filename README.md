[![pdm-managed](https://img.shields.io/endpoint?url=https%3A%2F%2Fcdn.jsdelivr.net%2Fgh%2Fpdm-project%2F.github%2Fbadge.json)](https://pdm-project.org)
![Test Status](https://github.com/AuScope-Cat/actions/workflows/python-publish.yml/badge.svg)

# AuScope Catalogue
Home of 'auscopecat', a Python package that aims to allow access to AuScope's catalogue of geoscience datasets from sources all over Australia

## Development

### To install

1. Install Python v3.10 or higher (https://www.python.org/)
2. Install PDM (https://pdm.fming.dev/latest/)
3. Clone this repository
4. 'pdm install' will install the python library dependencies

### To activate environment

```
eval $(pdm venv activate)
```
will start a Python env, 'deactivate' to exit

or

```
pdm run $SHELL
```
will run an environment in a new shell

### To search for WFS borehole datasets and download from one of them

```
$ pdm run $SHELL
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
pdm run pytest
```
in the 'AuScope-Cat'root directory


