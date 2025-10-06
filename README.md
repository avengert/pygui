# Professional Python Drag-and-Drop GUI Builder

A modern, intuitive drag-and-drop interface builder for creating CustomTkinter applications. This application provides a Visual Studio-like experience for designing Python GUI applications with a professional, modern interface.

## Features

### 🎨 Modern Interface
- **Dark/Light Theme Support**: Toggle between themes with system theme detection
- **Three-Panel Layout**: Widget toolbox, design canvas, and properties editor
- **Resizable Panels**: Adjust the interface to your workflow
- **Grid Snapping**: Optional grid system for precise widget placement

### 🧩 Core Widgets
The application supports 7 essential widgets with full property editing:

1. **Button** - With text, command binding, and size properties
2. **Label** - With text, font size, and positioning
3. **Entry** - Single-line text input with placeholder support
4. **Checkbox** - Toggle controls with text and state management
5. **Combobox** - Dropdown selection with custom options
6. **Slider** - Range controls with min/max values
7. **Progressbar** - Progress indicators with determinate/indeterminate modes

### 🖱️ Drag-and-Drop Functionality
- **Intuitive Widget Placement**: Drag widgets from toolbox to canvas
- **Visual Selection**: Click to select widgets with visual feedback
- **Resize Handles**: Interactive resize controls for selected widgets
- **Context Menus**: Right-click for delete, duplicate, and layer management
- **Keyboard Shortcuts**: Delete key for quick widget removal

### ⚙️ Properties Editor
- **Live Property Editing**: Real-time updates as you modify properties
- **Type-Safe Input**: Appropriate input controls for different property types
- **Comprehensive Properties**: Full control over widget appearance and behavior

### 🔧 Code Generation
- **Live Code View**: Real-time Python code generation
- **Export Functionality**: Save generated code as executable Python files
- **Clean Code Output**: Well-formatted, readable CustomTkinter code
- **Project Persistence**: Save and load design projects

### 👁️ Live Preview
- **Instant Preview**: Test your design without saving files
- **Separate Window**: Preview in isolated environment
- **Real Widget Rendering**: See exactly how your GUI will look

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup
1. Clone or download the project
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```

## Usage

### Getting Started
1. **Launch the Application**: Run `python main.py`
2. **Choose a Widget**: Click on any widget in the left toolbox
3. **Design Your Interface**: Drag widgets onto the center canvas
4. **Customize Properties**: Select widgets and edit properties in the right panel
5. **Preview Your Design**: Use the Preview button to test your GUI
6. **Export Your Code**: Save your design as a Python file

### Keyboard Shortcuts
- **Delete**: Remove selected widget
- **Right-click**: Open context menu for widget operations

### Menu Options
- **File**: New, Open, Save, Export Python
- **View**: Toggle grid, themes, code view
- **Tools**: Preview, clear canvas

## Architecture

The application follows a clean MVC architecture:

- **Model**: Widget data structures and property management
- **View**: CustomTkinter UI components and canvas rendering
- **Controller**: Event handling and business logic

### Key Components
- **WidgetToolbox**: Left panel with draggable widgets
- **DesignCanvas**: Center panel for visual design
- **PropertiesEditor**: Right panel for property editing
- **CodeGenerator**: Python code generation engine

## Supported Widget Properties

### Button
- Text content
- Width and height
- Command binding

### Label
- Text content
- Font size
- Dimensions

### Entry
- Placeholder text
- Size properties

### Checkbox
- Text label
- Checked state
- Dimensions

### Combobox
- Option values
- Size properties

### Slider
- Min/max values
- Current value
- Dimensions

### Progressbar
- Mode (determinate/indeterminate)
- Progress value
- Dimensions

## Project Structure

```
pygui/
├── main.py              # Main application file
├── requirements.txt     # Python dependencies
└── README.md           # This documentation
```

## Dependencies

- **customtkinter**: Modern Tkinter with dark theme support
- **pillow**: Image processing for enhanced UI elements

## Contributing

This is a professional-grade GUI builder designed for:
- **Developers**: Rapid GUI prototyping
- **Designers**: Visual interface creation
- **Students**: Learning GUI development concepts
- **Professionals**: Creating production-ready interfaces

## License

This project is open source and available under the MIT License.

## Future Enhancements

- Additional widget types
- Layout manager support
- Custom styling options
- Plugin architecture
- Collaboration features
- Version control integration

---

**Built with ❤️ using Python and CustomTkinter**
