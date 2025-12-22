# Installation Guide

## Requirements

- Python 3.9 or higher
- pip or conda package manager

## Basic Installation

```bash
pip install semantic-objects
```

## Installation with Optional Dependencies

For full functionality including BuildingMOTIF integration:

```bash
pip install semantic-objects[buildingmotif]
```

For development and testing:

```bash
pip install semantic-objects[dev]
```

For all optional dependencies:

```bash
pip install semantic-objects[all]
```

## Development Installation

If you want to contribute or modify the library:

```bash
# Clone the repository
git clone https://github.com/your-org/semantic-objects.git
cd semantic-objects

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .[dev]
```

## Dependencies

### Core Dependencies

- **rdflib** (>=7.1.3) - RDF graph handling and SPARQL queries
- **pandas** (>=2.0.3) - DataFrame operations for query results
- **pydantic** (>=2.0.0) - Data validation and type hints

### Optional Dependencies

- **buildingmotif** (>=0.3.0) - Template generation and model building
- **pyshacl** (>=0.26.0) - SHACL validation
- **semantic-mpc-interface** - Namespace definitions and utilities
- **brick-tq-shacl** - Brick schema support

### Development Dependencies

- **pytest** (>=7.0.0) - Testing framework
- **pytest-cov** - Coverage reporting
- **black** - Code formatting
- **flake8** - Linting
- **mypy** - Type checking
- **jupyter** - Notebook support

## Verification

Test your installation:

```python
# Test basic imports
from semantic_objects.s223 import Space, Window, Area
from semantic_objects.model_loader import ModelLoader
from semantic_objects.core import export_templates

# Create a simple space
space = Space(area=100.0)
print(f"Created space with area: {space.area.value} {space.area.unit}")

# Test template generation
space_yaml = space.generate_yaml_template()
print("✅ Installation successful!")
```

## Troubleshooting

### Common Issues

**ImportError: No module named 'buildingmotif'**
```bash
pip install buildingmotif
```

**ImportError: No module named 'semantic_mpc_interface'**
```bash
pip install semantic-mpc-interface
```

**RDF parsing errors**
```bash
pip install --upgrade rdflib
```

### Platform-Specific Notes

**Windows**
- Use `venv\Scripts\activate` instead of `source venv/bin/activate`
- Some dependencies may require Visual Studio Build Tools

**macOS**
- May need to install Xcode Command Line Tools: `xcode-select --install`

**Linux**
- Install system dependencies: `sudo apt-get install python3-dev`

### Virtual Environment Setup

Using conda:
```bash
conda create -n semantic-objects python=3.9
conda activate semantic-objects
pip install semantic-objects[all]
```

Using virtualenv:
```bash
python -m venv semantic-objects-env
source semantic-objects-env/bin/activate
pip install semantic-objects[all]
```

## Next Steps

1. **Quick Start**: Follow the [Quick Start Guide](quick-start.md)
2. **Tutorial**: Work through the [Basic Tutorial](../tutorial/basic-tutorial.ipynb)
3. **Examples**: Explore the [examples directory](../examples/)
4. **Documentation**: Read the [Core Concepts](core-concepts.md)