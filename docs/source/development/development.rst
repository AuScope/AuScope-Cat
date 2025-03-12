Development
===========

This page provides information for developers who want to contribute to AuScope-Cat.

Setting Up a Development Environment
---------------------------------

1. Clone the repository:

.. code-block:: bash

    git clone https://github.com/AuScope/AuScope-Cat.git
    cd AuScope-Cat

2. Create a virtual environment and install the package in development mode:

.. code-block:: bash

    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -e .

3. Install development dependencies:

.. code-block:: bash

    pip install pytest pytest-mock

Running Tests
-----------

To run the test suite:

.. code-block:: bash

    pytest

Code Style
---------

AuScope-Cat follows PEP 8 style guidelines. Please ensure your code adheres to these guidelines before submitting a pull request.

Building Documentation
-------------------

To build the documentation locally:

1. Install documentation dependencies:

.. code-block:: bash

    pip install -r docs/requirements.txt

2. Build the documentation:

.. code-block:: bash

    cd docs
    make html

The documentation will be available in the `docs/build/html` directory. 