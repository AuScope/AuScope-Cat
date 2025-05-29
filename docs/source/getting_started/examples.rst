Examples
========

This page provides examples of how to use AuScope-Cat for various common tasks.

Basic Search Example
--------------------

.. code-block:: python

    from auscopecat.api import search
    
    # Search for datasets containing "gold"
    results = search("gold")
    
    # Print the results
    for result in results:
        print(f"URL: {result.url}")
        print(f"Type: {result.type}")
        print("---")

Filtering by Service Type
-------------------------

.. code-block:: python

    from auscopecat.api import search
    from auscopecat.auscopecat_types import ServiceType
    
    # Search for WFS services containing "gold"
    wfs_results = search("gold", ogc_types=[ServiceType.WFS])
    
    # Print the results
    for result in wfs_results:
        print(f"URL: {result.url}")
        print(f"Type: {result.type}")
        print(f"WFS Type Name: {result.wfs_typename}")
        print("---")

Downloading Data
----------------

.. code-block:: python

    from auscopecat.api import search, download
    from auscopecat.auscopecat_types import DownloadType
    
    # Search for datasets
    results = search("gold")
    
    # Define a bounding box
    bbox = {
        "north": -30.0,
        "south": -35.0,
        "east": 150.0,
        "west": 145.0
    }
    
    # Download data for the first result
    if results:
        download(results[0], DownloadType.CSV, bbox=bbox, file_name="gold_data.csv") 