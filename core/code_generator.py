#!/usr/bin/env python3
"""
Code generator for the GUI Builder application.
"""

from typing import Dict
from models.widget_types import WidgetData, WidgetType


class CodeGenerator:
    """Generates Python code from widget data"""
    
    @staticmethod
    def clean_widget_id(widget_id: str) -> str:
        """Clean widget ID for use as Python variable name"""
        # Replace hyphens with underscores and ensure it starts with a letter or underscore
        clean_id = widget_id.replace('-', '_')
        
        # Ensure the ID starts with a letter or underscore (Python variable naming rules)
        if clean_id and not (clean_id[0].isalpha() or clean_id[0] == '_'):
            clean_id = '_' + clean_id
        
        return clean_id
    
    @staticmethod
    def validate_generated_code(code: str) -> tuple[bool, str]:
        """Validate generated Python code for syntax errors"""
        try:
            compile(code, '<string>', 'exec')
            return True, "Code is valid"
        except SyntaxError as e:
            return False, f"Syntax error: {str(e)}"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    @staticmethod
    def generate_code(widgets: Dict[str, WidgetData], window_properties: dict = None) -> str:
        """Generate Python code for the widgets with window properties"""
        if window_properties is None:
            window_properties = {
                'title': 'Generated GUI',
                'width': 800,
                'height': 600,
                'resizable': True,
                'min_width': 400,
                'min_height': 300,
                'center_on_screen': True,
                'auto_fit': True
            }
        
        # Calculate auto-fit dimensions if needed
        if window_properties.get('auto_fit', True) and widgets:
            max_x = max(widget.x + widget.width for widget in widgets.values()) + 50
            max_y = max(widget.y + widget.height for widget in widgets.values()) + 50
            window_width = max(window_properties['width'], max_x)
            window_height = max(window_properties['height'], max_y)
        else:
            window_width = window_properties['width']
            window_height = window_properties['height']
        
        imports = [
            "#!/usr/bin/env python3",
            '"""',
            "Generated GUI Application",
            "Created with Professional Python GUI Builder MVP",
            '"""',
            "",
            "import customtkinter as ctk",
            "import tkinter as tk",
            "",
            "# Set appearance mode and color theme",
            "ctk.set_appearance_mode('dark')",
            "ctk.set_default_color_theme('blue')",
            "",
            "class GeneratedApp(ctk.CTk):",
            '    """Generated GUI Application"""',
            "    ",
            "    def __init__(self):",
            "        super().__init__()",
            f"        self.title('{window_properties['title']}')",
        ]
        
        # Add window configuration
        if not window_properties.get('resizable', True):
            imports.append("        self.resizable(False, False)")
        
        # Add minimum size constraints
        min_width = window_properties.get('min_width', 400)
        min_height = window_properties.get('min_height', 300)
        imports.append(f"        self.minsize({min_width}, {min_height})")
        
        # Force the window size
        imports.append(f"        self.geometry('{window_width}x{window_height}')")
        imports.append("        self.update_idletasks()  # Force window to update")
        imports.append("        self.state('normal')  # Ensure window is not minimized")
        imports.append(f"        self.geometry('{window_width}x{window_height}')  # Set size again")
        imports.append("        self.update_idletasks()")
        
        imports.extend([
            "        self.setup_ui()",
            "        # Use after to delay size enforcement",
            f"        self.after(100, self.enforce_window_size)",
            f"        self.after(200, self.center_window)",
            "",
            "    def enforce_window_size(self):",
            '        """Aggressively enforce the window size"""',
            f"        self.geometry('{window_width}x{window_height}')",
            "        self.update_idletasks()",
            f"        self.tk.call('wm', 'geometry', self._w, '{window_width}x{window_height}')",
            "        self.update_idletasks()",
            "        self.state('normal')",
            f"        self.geometry('{window_width}x{window_height}')",
            "        self.update_idletasks()",
            "        try:",
            f"            self.configure(width={window_width}, height={window_height})",
            "            self.update_idletasks()",
            "        except:",
            "            pass",
            f"        self.geometry('{window_width}x{window_height}')",
            "        self.update_idletasks()",
            "",
            "    def setup_ui(self):",
            '        """Setup the user interface"""',
        ])
        
        # Add centering after setup_ui if needed
        if window_properties.get('center_on_screen', True):
            imports.extend([
                "        # Center window on screen after UI is set up",
                "        self.center_window()",
                "        ",
                "    def center_window(self):",
                "        \"\"\"Center the window on screen\"\"\"",
                "        self.update_idletasks()",
                "        # Force window to correct size multiple times to ensure it sticks",
                f"        self.geometry('{window_width}x{window_height}')",
                "        self.update_idletasks()",
                f"        self.geometry('{window_width}x{window_height}')  # Set again to ensure it sticks",
                "        self.update_idletasks()",
                "        ",
                "        # Get actual dimensions",
                "        width = self.winfo_width()",
                "        height = self.winfo_height()",
                "        ",
                "        # If window is still too small, force it again",
                f"        if width < {window_width-100} or height < {window_height-100}:",
                f"            self.geometry('{window_width}x{window_height}')",
                "            self.update_idletasks()",
                "            width = self.winfo_width()",
                "            height = self.winfo_height()",
                "        ",
                "        # Center the window",
                "        x = (self.winfo_screenwidth() // 2) - (width // 2)",
                "        y = (self.winfo_screenheight() // 2) - (height // 2)",
                "        self.geometry(f'{width}x{height}+{x}+{y}')",
            ])
        
        widget_code = []
        
        for widget_data in widgets.values():
            widget_code.append(CodeGenerator.generate_widget_code(widget_data))
        
        # Combine all code
        all_code = imports + widget_code + [
            "",
            "if __name__ == '__main__':",
            "    app = GeneratedApp()",
            "    app.mainloop()"
        ]
        
        return "\n".join(all_code)
    
    @staticmethod
    def generate_widget_code(widget_data: WidgetData) -> str:
        """Generate code for a single widget"""
        props = widget_data.properties
        
        if widget_data.type == WidgetType.BUTTON:
            text = props["text"].value
            width = props["width"].value
            height = props["height"].value
            command = props["command"].value
            
            # Clean widget ID for Python variable name
            clean_id = CodeGenerator.clean_widget_id(widget_data.id)
            code_lines = [
                f"        # Button at ({widget_data.x}, {widget_data.y})",
                f"        self.button_{clean_id} = ctk.CTkButton(",
                f"            self, text='{text}', width={width}, height={height}"
            ]
            
            if command:
                code_lines.append(f"            , command={command}")
            
            code_lines.extend([
                f"        )",
                f"        self.button_{clean_id}.place(x={widget_data.x}, y={widget_data.y})"
            ])
            
            return "\n".join(code_lines)
            
        elif widget_data.type == WidgetType.LABEL:
            text = props["text"].value
            width = props["width"].value
            height = props["height"].value
            font_size = props["font_size"].value
            
            # Clean widget ID for Python variable name
            clean_id = CodeGenerator.clean_widget_id(widget_data.id)
            code_lines = [
                f"        # Label at ({widget_data.x}, {widget_data.y})",
                f"        self.label_{clean_id} = ctk.CTkLabel(",
                f"            self, text='{text}', width={width}, height={height},",
                f"            font=ctk.CTkFont(size={font_size})",
                f"        )",
                f"        self.label_{clean_id}.place(x={widget_data.x}, y={widget_data.y})"
            ]
            
            return "\n".join(code_lines)
            
        elif widget_data.type == WidgetType.ENTRY:
            placeholder = props["placeholder"].value
            width = props["width"].value
            height = props["height"].value
            
            # Clean widget ID for Python variable name
            clean_id = CodeGenerator.clean_widget_id(widget_data.id)
            code_lines = [
                f"        # Entry at ({widget_data.x}, {widget_data.y})",
                f"        self.entry_{clean_id} = ctk.CTkEntry(",
                f"            self, placeholder_text='{placeholder}', width={width}, height={height}",
                f"        )",
                f"        self.entry_{clean_id}.place(x={widget_data.x}, y={widget_data.y})"
            ]
            
            return "\n".join(code_lines)
            
        elif widget_data.type == WidgetType.CHECKBOX:
            text = props["text"].value
            checked = props["checked"].value
            width = props["width"].value
            height = props["height"].value
            
            # Clean widget ID for Python variable name
            clean_id = CodeGenerator.clean_widget_id(widget_data.id)
            code_lines = [
                f"        # Checkbox at ({widget_data.x}, {widget_data.y})",
                f"        self.checkbox_{clean_id} = ctk.CTkCheckBox(",
                f"            self, text='{text}', width={width}, height={height}",
                f"        )"
            ]
            
            if checked:
                code_lines.append(f"        self.checkbox_{clean_id}.select()")
            
            code_lines.append(f"        self.checkbox_{clean_id}.place(x={widget_data.x}, y={widget_data.y})")
            
            return "\n".join(code_lines)
            
        elif widget_data.type == WidgetType.COMBOBOX:
            values = props["values"].value
            width = props["width"].value
            height = props["height"].value
            
            # Clean widget ID for Python variable name
            clean_id = CodeGenerator.clean_widget_id(widget_data.id)
            code_lines = [
                f"        # Combobox at ({widget_data.x}, {widget_data.y})",
                f"        self.combobox_{clean_id} = ctk.CTkComboBox(",
                f"            self, values={values.split(',')}, width={width}, height={height}",
                f"        )",
                f"        self.combobox_{clean_id}.place(x={widget_data.x}, y={widget_data.y})"
            ]
            
            return "\n".join(code_lines)
            
        elif widget_data.type == WidgetType.SLIDER:
            from_val = props["from_"].value
            to_val = props["to"].value
            value = props["value"].value
            width = props["width"].value
            height = props["height"].value
            
            # Clean widget ID for Python variable name
            clean_id = CodeGenerator.clean_widget_id(widget_data.id)
            code_lines = [
                f"        # Slider at ({widget_data.x}, {widget_data.y})",
                f"        self.slider_{clean_id} = ctk.CTkSlider(",
                f"            self, from_={from_val}, to={to_val}, width={width}, height={height}",
                f"        )",
                f"        self.slider_{clean_id}.set({value})",
                f"        self.slider_{clean_id}.place(x={widget_data.x}, y={widget_data.y})"
            ]
            
            return "\n".join(code_lines)
            
        elif widget_data.type == WidgetType.PROGRESSBAR:
            mode = props["mode"].value
            value = props["value"].value
            width = props["width"].value
            height = props["height"].value
            
            # Clean widget ID for Python variable name
            clean_id = CodeGenerator.clean_widget_id(widget_data.id)
            code_lines = [
                f"        # Progressbar at ({widget_data.x}, {widget_data.y})",
                f"        self.progressbar_{clean_id} = ctk.CTkProgressBar(",
                f"            self, width={width}, height={height}",
                f"        )"
            ]
            
            if mode == "determinate":
                code_lines.append(f"        self.progressbar_{clean_id}.set({value/100})")
            
            code_lines.append(f"        self.progressbar_{clean_id}.place(x={widget_data.x}, y={widget_data.y})")
            
            return "\n".join(code_lines)
        
        return ""
