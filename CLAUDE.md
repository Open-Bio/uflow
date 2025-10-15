# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

uflow is a runtime-extendable Python Qt-based node editor framework for visual programming. It follows a plugin-based architecture where functionality is organized into packages, each containing nodes (computational units), pins (data types), function libraries, UI components, tools, and factories.

## Development Commands

### Installation and Setup

```bash
# Install dependencies using uv (recommended)
uv sync

# Run uflow standalone
uv run python uflow.py

# Run uflow with MDI interface
uv run python uflow-mdi.py

# Load a specific graph file
uv run python uflow.py -f path/to/file.pygraph
```

### Testing

```bash
# Run all tests using pytest
uv run pytest

# Run all tests using unittest
uv run python unittest_runner.py

# Run specific test file
uv run pytest uflow/Tests/Test_General.py

# Run with verbosity
uv run pytest -v
```

### Code Quality

```bash
# Format code with black
uv run black uflow/

# Run type checking
uv run mypy uflow/

# Lint with flake8
uv run flake8 uflow/
```

### Documentation

```bash
# Build documentation
cd docs
sphinx-build -b html source build

# Regenerate API documentation after code changes
cd docs
sphinx-apidoc -f -o source/ ../uflow ../uflow/UI/resources.py
sphinx-build -b html source build

# View docs: open docs/build/html/index.html
```

## Architecture

### Core System (`uflow/Core/`)

- **PackageBase.py**: Base class for all packages. Packages inherit from this and call `analyzePackage()` to auto-register components
- **NodeBase.py**: Base class for class-based nodes with full lifecycle management, state, and custom UI support
- **PinBase.py**: Base class for custom pin types (data types)
- **FunctionLibrary.py**: Base for function libraries that use `@IMPLEMENT_NODE` decorator for functional nodes
- **GraphBase.py**: Graph structure management
- **GraphManager.py**: Manages multiple graphs and execution
- **Common.py**: Common types, enums (NodeTypes, PinOptions, StructureType, etc.)

### Package System (`uflow/Packages/`)

Packages are self-contained plugin modules with standard directory structure:

```
PackageName/
├── __init__.py              # Must inherit PackageBase
├── Nodes/                   # Class-based nodes (complex, stateful)
├── Pins/                    # Custom data types
├── FunctionLibraries/       # Functional nodes (@IMPLEMENT_NODE decorator)
├── UI/                      # Custom UI for nodes/pins
├── Factories/               # UINodeFactory, UIPinFactory, PinInputWidgetFactory
├── Tools/                   # ShelfTools (toolbar) and DockTools (panels)
├── Exporters/               # Import/export handlers
└── PrefsWidgets/            # Settings panels
```

**Key packages:**

- **uflowBase**: Core nodes (math, logic, control flow, variables)
- **uflowDataAnalysis**: DataFrame processing, CSV I/O, data viewers
- **uflowOpenCv**: Computer vision nodes wrapping OpenCV

### Node Implementation Patterns

**Two approaches to creating nodes:**

1. **Class-based Nodes** (`Nodes/` directory)
   - Inherit from `NodeBase`
   - Use for complex logic, stateful operations, custom UI, dynamic pin management
   - Define `__init__`, `compute()`, `category()`, `keywords()`, `pinTypeHints()`
   - Can create ExecPins for execution flow control
   - Example: ViewerNode, DataViewerNode

2. **Functional Nodes** (`FunctionLibraries/` directory)
   - Use `@IMPLEMENT_NODE` decorator on static methods in FunctionLibraryBase subclass
   - Use for simple, pure functions: math ops, data transforms, I/O
   - Parameters as tuples: `param=('PinType', default_value)`
   - Use `REF` for output parameters: `output=(REF, ('PinType', default_value))`
   - Example: ReadCSV, WriteCSV, cv_ReadImage

**General rule:** Use functional nodes for simple transformations; use class-based nodes for complex state management.

### Pin System

Custom data types require:

- Pin class inheriting from `PinBase`
- Static methods: `supportedDataTypes()`, `color()`, `internalDataStructure()`, `processData()`
- For non-serializable data (like DataFrames, images): use `NoneEncoder`/`NoneDecoder` and disable `PinOptions.Storable`
- Pin colors identify types visually in the UI

### AI Code Generation System (`uflow/AI/`)

The AI integration generates pure function nodes on-demand:

- **config.py**: Manages AI configuration (API keys, endpoints)
- **openai_client.py**: Validates prompts and generated code for security
- **service.py**: Defines AIServiceInterface
- All generated code is validated to prevent execution flow in pure function nodes (no ExecPin, no .call())

## Important Development Notes

### Package Development

- Package class name must match directory name
- Each subdirectory needs `__init__.py` with pkgutil path extension
- Call `self.analyzePackage(os.path.dirname(__file__))` in package `__init__`
- Use clear categories and keywords for node discoverability

### Pin Data Flow

- Input pins: `self.createInputPin(name, pinType, defaultValue)`
- Output pins: `self.createOutputPin(name, pinType)`
- Get data: `pin.getData()`
- Set data: `pin.setData(value)`
- Check if updated: `pin.dirty`
- Pin structures: `StructureType.Single`, `StructureType.Array`, `StructureType.Multi`

### Execution Flow

- Nodes with ExecPins control execution order
- Use `DEFAULT_IN_EXEC_NAME` and `DEFAULT_OUT_EXEC_NAME` constants
- Trigger downstream: `self.outExec.call()`
- Pure function nodes should NOT use ExecPins

### UI Integration

- Tools access uflow instance: `self._wrapper.canvasRef().uflowInstance`
- Invoke dock tools: `uflowInstance.invokeDockToolByName(packageName, toolName)`
- DockTool requires: `name()`, `toolTip()`, `isSingleton()` static methods
- ShelfTool requires: `name()`, `toolTip()`, `getIcon()`, `do()` method

### Configuration Management

- ConfigManager is singleton managing QSettings-based configs
- Input bindings: `uflow/Configs/input.json`
- Preferences: accessed via `ConfigManager().getPrefsValue(alias, key)`

### Error Handling

- Nodes should handle exceptions gracefully in `compute()`
- Print errors to console or use logging
- Validate inputs before processing
- Provide meaningful error messages

## Common Patterns

### Creating a New Package

1. Create directory structure under `uflow/Packages/YourPackage/`
2. Write `__init__.py` inheriting `PackageBase`
3. Add nodes/pins/function libraries as needed
4. Create UI factories if custom UI required
5. Add tools if interactive features needed

### Adding a Custom Data Type

1. Define data class
2. Create pin class in `Pins/` inheriting `PinBase`
3. Implement required static methods
4. For complex objects: use `NoneEncoder`/`NoneDecoder`, disable `PinOptions.Storable`

### Adding Function Library Nodes

1. Create class inheriting `FunctionLibraryBase`
2. Add `@staticmethod` methods with `@IMPLEMENT_NODE` decorator
3. Set `meta={NodeMeta.CATEGORY: '...', NodeMeta.KEYWORDS: [...]}`
4. Use `nodeType=NodeTypes.Callable` for exec-based nodes
5. Use `returns=None` with REF outputs for multiple outputs

### Testing Nodes

- Test files in `uflow/Tests/` follow `Test_*.py` naming
- Import test infrastructure from `uflow.Tests.TestsBase`
- Create graphs programmatically for testing
- Test both data flow and execution flow

## File Locations

- Entry points: `uflow.py`, `uflow-mdi.py`
- App logic: `uflow/App.py`, `uflow/AppMDI.py`
- Core framework: `uflow/Core/`
- Packages: `uflow/Packages/`
- UI components: `uflow/UI/`
- Tests: `uflow/Tests/`
- Configuration: `uflow/Configs/`
- Documentation: `docs/`
- Development guides: `notes/` (detailed Chinese guides on package development, node types, etc.)

## Dependencies

Core: PySide6, qtpy, blinker, SQLAlchemy, pandas, openai
Dev: pytest, pytest-qt, black, flake8, mypy, sphinx, sphinx_rtd_theme

Note: Uses Tsinghua PyPI mirror by default (see pyproject.toml)
