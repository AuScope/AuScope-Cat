Tutorials
=========

This section provides step-by-step tutorials for common tasks with AuScope-Cat.

Getting Started with AuScope-Cat
------------------------------

This tutorial will guide you through the basic usage of AuScope-Cat to search for and download geoscience datasets.

1. Installation
^^^^^^^^^^^^^

First, install AuScope-Cat using pip:

.. code-block:: bash

    pip install auscopecat

2. Basic Search
^^^^^^^^^^^^^

Let's start by searching for datasets related to gold:

.. code-block:: python

    from auscopecat.api import search
    
    # Search for datasets containing "gold"
    results = search("gold")
    
    # Print the number of results
    print(f"Found {len(results)} datasets")
    
    # Print the first 5 results
    for result in results[:5]:
        print(f"URL: {result.url}")
        print(f"Type: {result.type}")
        print("---")

3. Filtering Results
^^^^^^^^^^^^^^^^^

You can filter results by service type:

.. code-block:: python

    from auscopecat.api import search
    from auscopecat.auscopecat_types import ServiceType
    
    # Search for WFS services containing "gold"
    wfs_results = search("gold", ogc_type=ServiceType.WFS)
    
    # Print the number of results
    print(f"Found {len(wfs_results)} WFS datasets")

4. Downloading Data
^^^^^^^^^^^^^^^^

Once you've found a dataset, you can download it:

.. code-block:: python

    from auscopecat.api import download
    from auscopecat.auscopecat_types import DownloadType
    
    # Define a bounding box
    bbox = {
        "north": -30.0,
        "south": -35.0,
        "east": 150.0,
        "west": 145.0
    }
    
    # Download data for the first result
    if wfs_results:
        download(wfs_results[0], DownloadType.CSV, bbox=bbox, file_name="gold_data.csv")
        print("Data downloaded to gold_data.csv") 