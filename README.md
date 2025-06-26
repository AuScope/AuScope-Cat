![Test Status](https://github.com/AuScope/AuScope-Cat/actions/workflows/python-build-test.yml/badge.svg)
[![Coverage Status](https://raw.githubusercontent.com/AuScope/AuScope-Cat/main/.github/badges/coverage.svg)](https://github.com/AuScope/AuScope-Cat/actions/workflows/python-build-test.yml)

# AuScope Catalogue
Home of 'auscopecat', a Python package that allows access to AuScope's catalogue of geoscience datasets from sources all over Australia

## Install

'auscopecat' is available from PyPi https://pypi.org/project/auscopecat/

```
pip install auscopecat
```

## Jupyter Notebooks

We have created a set of [Jupyter notebooks](https://github.com/AuScope/AuScope-Cat/tree/main/jupyter-notebooks) to demonstrate some of 'auscopecat's applications 

## Documentation

'auscopecat's documentation is available [here](auscope.github.io/AuScope-Cat/)

## Development

### To install

1. Install Python v3.10 or higher (https://www.python.org/)
2. Install uv (https://docs.astral.sh/uv/getting-started/installation/)
3. Clone this repository

### To create and activate a new Python environment

```
uv venv
source .venv/bin/activate
uv sync
```

And to deactivate:
```
deactivate
```

**ALSO**

```
uv run $SHELL
```
will run an environment in a new shell

**TIP**: Use 'uv pip install "auscopecat@."' to install the local auscopecat package

### Pre-commit
This project comes with a pre-commit configuration `pre-commit install` to add it as a git hook.<br>
If you want to let Ruff fix a lot of the problems for you, you can use `ruff check . --fix`

### To search for WFS borehole datasets and download from one of them

```
$ uv run $SHELL
$ uv pip install "auscopecat@."
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

## Reference used to cite 'auscopecat'

Please cite 'auscopecat' in your publications if you use it in your research  

*Fazio, Vincent; Woodman, Stuart; Jiang, Lingbo; Li, Yunlong; Warren, Peter. AuScope AVRE Technical Workshop 2025: auscopecat - A python package to access AuScope's resources and beyond. In: AuScope AVRE Technical Workshop 2025; 13 to end of 13 Jun 2025; Virtual. AuScope Pty Ltd; 2025. 18pp. csiro:EP2025-2482. https://doi.org/10.5281/zenodo.15654067*
