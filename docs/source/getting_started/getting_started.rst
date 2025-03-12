Getting Started
==============

Quick Start
----------

AuScope-Cat provides easy access to geoscience datasets from sources all over Australia. Here's how to get started quickly:

.. code-block:: python

    from auscopecat.api import search
    from auscopecat.auscopecat_types import ServiceType

    # Search for datasets containing "gold"
    results = search("gold")
    
    # Print the first 5 results
    for result in results[:5]:
        print(f"URL: {result.url}")
        print(f"Type: {result.type}")
        print("---")

Basic Concepts
-------------

AuScope-Cat allows you to:

1. **Search** for geoscience datasets using keywords
2. **Filter** results by service type (WFS, WMS, etc.)
3. **Download** data in various formats
4. **Process** the data using compatible tools

The main components of the library are:

- **search**: Find datasets matching your criteria
- **download**: Retrieve data from a specific service
- **ServiceType**: Enum for filtering by service type
- **DownloadType**: Enum for specifying download format 