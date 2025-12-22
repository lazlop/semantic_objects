# Semantic Objects Examples

This directory contains practical examples demonstrating the capabilities of the Semantic Objects library.

## 📁 Example Files

### [basic_usage.py](basic_usage.py)
**Beginner-friendly examples covering core functionality:**
- Creating semantic objects (Space, Window)
- Template generation and export
- Model building with BMotifSession
- Loading objects from RDF graphs
- SPARQL query generation
- SHACL validation shapes
- Working with units and properties

**Run it:**
```bash
python examples/basic_usage.py
```

### [advanced_patterns.py](advanced_patterns.py)
**Advanced patterns and custom entity creation:**
- Custom entity definitions (Office, ConferenceRoom)
- Inheritance hierarchies
- Complex model building
- Advanced querying and filtering
- Custom properties and constraints
- SHACL validation
- Complete round-trip workflows

**Run it:**
```bash
python examples/advanced_patterns.py
```

## 🎯 What Each Example Demonstrates

### Basic Usage Examples

1. **Creating Objects**: Simple Space and Window creation with properties
2. **Template Generation**: Export BuildingMOTIF templates to YAML files
3. **Model Building**: Use BMotifSession to generate RDF models
4. **Model Loading**: Load Python objects from existing RDF data
5. **Query Generation**: Automatic SPARQL query creation
6. **Validation**: Generate SHACL shapes for data validation
7. **Units & Properties**: Work with different units and quantity kinds

### Advanced Pattern Examples

1. **Custom Entities**: Define Office and ConferenceRoom classes
2. **Inheritance**: Demonstrate polymorphic behavior with class hierarchies
3. **Template Generation**: Advanced template patterns and dependencies
4. **Complex Models**: Build multi-entity models with relationships
5. **Advanced Querying**: Filter and analyze loaded objects
6. **Custom Properties**: Create domain-specific properties
7. **Validation**: SHACL constraint generation and validation
8. **Round-Trip**: Complete workflow from objects → RDF → objects

## 🚀 Quick Start

1. **Install the library:**
   ```bash
   pip install semantic-objects[buildingmotif]
   ```

2. **Run basic examples:**
   ```bash
   cd examples
   python basic_usage.py
   ```

3. **Explore advanced patterns:**
   ```bash
   python advanced_patterns.py
   ```

## 📊 Expected Output

### Basic Usage
- Creates semantic objects with properties
- Generates template files in `example_templates/`
- Builds RDF models with ~50-100 triples
- Loads objects back from RDF data
- Shows SPARQL queries and SHACL shapes

### Advanced Patterns
- Creates custom entity hierarchies
- Generates advanced templates in `advanced_templates/`
- Builds complex models with ~200-300 triples
- Demonstrates filtering and analysis
- Saves/loads complete building models

## 🔧 Customization

### Adding Your Own Examples

1. **Create a new Python file** in this directory
2. **Import the library:**
   ```python
   from semantic_objects.s223 import *
   from semantic_objects.core import semantic_object, required_field
   ```

3. **Define custom entities:**
   ```python
   @semantic_object
   class MyEntity(Node):
       my_property: MyProperty = required_field()
   ```

4. **Follow the patterns** from existing examples

### Common Patterns

**Entity Definition:**
```python
@semantic_object
class MySpace(Space):
    custom_field: CustomProperty = required_field()
    optional_field: Optional[str] = optional_field()
```

**Template Generation:**
```python
export_templates(MySpace, 'my_templates')
```

**Model Building:**
```python
session = BMotifSession()
session.load_class_templates(MySpace)
my_space = MySpace(area=100.0, custom_field=CustomProperty(42))
session.evaluate(my_space)
```

**Model Loading:**
```python
loader = ModelLoader(source='my_model.ttl')
spaces = loader.load_instances(MySpace, ontology='s223')
```

## 📚 Related Documentation

- [Quick Start Guide](../docs/quick-start.md)
- [Core Concepts](../docs/core-concepts.md)
- [Basic Tutorial](../tutorial/basic-tutorial.ipynb)
- [Model Loading Tutorial](../tutorial/model-loading-tutorial.ipynb)
- [Template Generation Tutorial](../tutorial/template-generation-tutorial.ipynb)

## 🐛 Troubleshooting

**Import errors:**
```bash
pip install semantic-objects[buildingmotif]
```

**Template generation fails:**
- Check that all required fields have proper types
- Ensure custom entities inherit from appropriate base classes

**Model loading issues:**
- Verify RDF data contains expected entity types
- Check ontology parameter matches your data (usually 's223')

**SPARQL query errors:**
- Ensure graph contains data in expected format
- Check namespace bindings in your RDF data

## 💡 Tips

1. **Start with basic_usage.py** to understand core concepts
2. **Modify examples** to experiment with different patterns
3. **Check generated files** (templates, RDF) to understand output
4. **Use type hints** for better IDE support and error catching
5. **Follow naming conventions** for consistency with S223 ontology