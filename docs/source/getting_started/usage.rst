Usage
=====

Basic Usage
----------

Here's a simple example of how to use AuScope-Cat to search for datasets:

.. code-block:: python

    from auscopecat.api import search
    from auscopecat.auscopecat_types import ServiceType

    # Search for datasets containing "gold"
    results = search("gold")

    # Search for WFS services containing "gold"
    wfs_results = search("gold", ogc_type=ServiceType.WFS)

    # Print the results
    for result in results:
        print(f"URL: {result.url}")
        print(f"Type: {result.type}")
        if hasattr(result, "wfs_typename"):
            print(f"WFS Type Name: {result.wfs_typename}")
        print("---")

Downloading Data
---------------

You can download data using the download function:

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
    download(results[0], DownloadType.CSV, bbox=bbox, file_name="my_data.csv") 