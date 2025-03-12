# AuScope-Cat Documentation

This directory contains the documentation for the AuScope-Cat package.

## Building the Documentation Locally

To build the documentation locally, follow these steps:

1. Install the documentation dependencies:

```bash
pip install -r requirements.txt
```

2. Build the documentation:

```bash
cd docs
make html
```

3. View the documentation:

The built documentation will be available in the `build/html` directory. You can open `build/html/index.html` in your web browser to view it.

## Documentation Structure

The documentation is organized into the following sections:

- **GETTING STARTED**: Basic information for users to get started with AuScope-Cat
  - Installation
  - Getting Started
  - Examples
  - Tutorials
  - Citation

- **DEVELOPMENT**: Information for developers who want to contribute to AuScope-Cat
  - Development
  - Changelog
  - Roadmap
  - Code of Conduct
  - Contributing
  - Contributors

- **API REFERENCE**: Detailed API documentation
  - API
  - Modules

## Updating the Documentation

To update the documentation:

1. Edit the relevant `.rst` files in the `source` directory
2. Build the documentation to preview your changes
3. Commit your changes and push them to GitHub
4. The GitHub Action will automatically build and deploy the documentation to GitHub Pages 