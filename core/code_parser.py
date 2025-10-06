#!/usr/bin/env python3
"""
Code parser for the GUI Builder application.
"""

from typing import Dict, List, Optional, Any
from models.widget_types import WidgetType, WidgetProperty, WidgetData


class CodeParser:
    """Parses Python code to extract widget data"""
    
    @staticmethod
    def parse_code_to_widgets(code: str) -> tuple[Dict[str, WidgetData], dict]:
        """Parse generated code and extract widget data and window properties"""
        print(f"DEBUG: parse_code_to_widgets called with {len(code)} characters")
        widgets = {}
        window_properties = {
            'title': 'Generated GUI',
            'width': 800,
            'height': 600,
            'resizable': True,
            'min_width': 400,
            'min_height': 300,
            'center_on_screen': True
        }
        
        try:
            lines = code.split('\n')
            in_setup_ui = False
            current_widget_lines = []
            
            print(f"DEBUG: Processing {len(lines)} lines")
            
            for i, line in enumerate(lines):
                line = line.strip()
                
                # Extract window properties
                if "self.title(" in line:
                    title = CodeParser._extract_string_value(line)
                    if title:
                        window_properties['title'] = title
                        print(f"DEBUG: Found title: {title}")
                elif "self.geometry(" in line:
                    geometry = CodeParser._extract_string_value(line)
                    if geometry and 'x' in geometry:
                        width, height = geometry.split('x')
                        window_properties['width'] = int(width)
                        window_properties['height'] = int(height)
                        print(f"DEBUG: Found geometry: {width}x{height}")
                
                # Check if we're in setup_ui method
                if "def setup_ui(self):" in line:
                    in_setup_ui = True
                    print("DEBUG: Entered setup_ui method")
                    continue
                elif line.startswith("def ") and in_setup_ui:
                    in_setup_ui = False
                    print("DEBUG: Exited setup_ui method")
                
                if not in_setup_ui:
                    continue
                
                # Check if this is a widget creation line (but not a .place() call)
                if any(f"self.{widget_type}_" in line for widget_type in ['button', 'label', 'entry', 'checkbox', 'combobox', 'slider', 'progressbar']) and not ".place(" in line:
                    print(f"DEBUG: Found widget creation line: {line}")
                    # Start collecting widget lines
                    current_widget_lines = [line]
                elif current_widget_lines and line.strip() == ")":
                    print(f"DEBUG: Found widget closing line: {line}")
                    # End of widget creation, add the closing parenthesis
                    current_widget_lines.append(line)
                    
                    # Look for the .place() call in the next few lines
                    place_line = None
                    for j in range(i+1, min(i+5, len(lines))):
                        if ".place(" in lines[j]:
                            place_line = lines[j].strip()
                            print(f"DEBUG: Found place line: {place_line}")
                            break
                    
                    # Parse the complete widget definition
                    print(f"DEBUG: Parsing widget block with {len(current_widget_lines)} lines")
                    widget_data = CodeParser._parse_widget_block(current_widget_lines, place_line)
                    if widget_data:
                        widgets[widget_data.id] = widget_data
                        print(f"DEBUG: Successfully parsed widget {widget_data.id}")
                    else:
                        print("DEBUG: Failed to parse widget")
                    
                    # Reset state after parsing
                    current_widget_lines = []
                elif current_widget_lines and not line.startswith("        #") and not line.startswith("        self.") and not line.strip() == "":
                    # Continue collecting widget lines (but not comments, other widget lines, or empty lines)
                    current_widget_lines.append(line)
                    print(f"DEBUG: Added line to widget block: {line}")
            
            print(f"DEBUG: Parsing complete, found {len(widgets)} widgets")
            return widgets, window_properties
            
        except Exception as e:
            print(f"DEBUG: Error parsing code: {e}")
            import traceback
            traceback.print_exc()
            return {}, window_properties
    
    @staticmethod
    def _extract_string_value(line: str) -> str:
        """Extract string value from a line like self.title('value')"""
        try:
            # Find the string between quotes
            start = line.find("'")
            if start == -1:
                start = line.find('"')
            if start == -1:
                return ""
            
            start += 1
            end = line.find("'", start)
            if end == -1:
                end = line.find('"', start)
            if end == -1:
                return ""
            
            return line[start:end]
        except:
            return ""
    
    @staticmethod
    def _parse_widget_block(widget_lines: List[str], place_line: str = None) -> Optional[WidgetData]:
        """Parse a complete widget definition block including .place() call"""
        try:
            # Combine all widget lines into a single string for parsing
            widget_text = " ".join(widget_lines)
            
            # Extract widget type and variable name
            if "self.button_" in widget_text:
                return CodeParser._parse_button_block(widget_text, place_line)
            elif "self.label_" in widget_text:
                return CodeParser._parse_label_block(widget_text, place_line)
            elif "self.entry_" in widget_text:
                return CodeParser._parse_entry_block(widget_text, place_line)
            elif "self.checkbox_" in widget_text:
                return CodeParser._parse_checkbox_block(widget_text, place_line)
            elif "self.combobox_" in widget_text:
                return CodeParser._parse_combobox_block(widget_text, place_line)
            elif "self.slider_" in widget_text:
                return CodeParser._parse_slider_block(widget_text, place_line)
            elif "self.progressbar_" in widget_text:
                return CodeParser._parse_progressbar_block(widget_text, place_line)
            
            return None
        except Exception as e:
            print(f"Error parsing widget block: {e}")
            return None
    
    @staticmethod
    def _parse_button_block(widget_text: str, place_line: str = None) -> WidgetData:
        """Parse button widget from complete widget block"""
        # Extract variable name and properties
        var_name = CodeParser._extract_variable_name(widget_text)
        widget_id = var_name.replace("button_", "")
        
        # Extract properties from the widget creation
        text = CodeParser._extract_property_value(widget_text, "text")
        width = CodeParser._extract_property_value(widget_text, "width", 100)
        height = CodeParser._extract_property_value(widget_text, "height", 30)
        
        # Extract position from .place() call
        x, y = 0, 0
        if place_line:
            x, y = CodeParser._extract_position(place_line)
        
        properties = {
            'text': WidgetProperty('text', text or 'Button', 'str'),
            'width': WidgetProperty('width', width, 'int'),
            'height': WidgetProperty('height', height, 'int')
        }
        
        return WidgetData(
            id=widget_id,
            type=WidgetType.BUTTON,
            x=x, y=y, width=width, height=height,
            properties=properties
        )
    
    @staticmethod
    def _parse_label_block(widget_text: str, place_line: str = None) -> WidgetData:
        """Parse label widget from complete widget block"""
        var_name = CodeParser._extract_variable_name(widget_text)
        widget_id = var_name.replace("label_", "")
        
        text = CodeParser._extract_property_value(widget_text, "text")
        width = CodeParser._extract_property_value(widget_text, "width", 200)
        height = CodeParser._extract_property_value(widget_text, "height", 30)
        
        x, y = 0, 0
        if place_line:
            x, y = CodeParser._extract_position(place_line)
        
        properties = {
            'text': WidgetProperty('text', text or 'Label', 'str'),
            'width': WidgetProperty('width', width, 'int'),
            'height': WidgetProperty('height', height, 'int')
        }
        
        return WidgetData(
            id=widget_id,
            type=WidgetType.LABEL,
            x=x, y=y, width=width, height=height,
            properties=properties
        )
    
    @staticmethod
    def _parse_entry_block(widget_text: str, place_line: str = None) -> WidgetData:
        """Parse entry widget from complete widget block"""
        var_name = CodeParser._extract_variable_name(widget_text)
        widget_id = var_name.replace("entry_", "")
        
        placeholder = CodeParser._extract_property_value(widget_text, "placeholder_text")
        width = CodeParser._extract_property_value(widget_text, "width", 200)
        height = CodeParser._extract_property_value(widget_text, "height", 30)
        
        x, y = 0, 0
        if place_line:
            x, y = CodeParser._extract_position(place_line)
        
        properties = {
            'placeholder_text': WidgetProperty('placeholder_text', placeholder or '', 'str'),
            'width': WidgetProperty('width', width, 'int'),
            'height': WidgetProperty('height', height, 'int')
        }
        
        return WidgetData(
            id=widget_id,
            type=WidgetType.ENTRY,
            x=x, y=y, width=width, height=height,
            properties=properties
        )
    
    @staticmethod
    def _parse_checkbox_block(widget_text: str, place_line: str = None) -> WidgetData:
        """Parse checkbox widget from complete widget block"""
        var_name = CodeParser._extract_variable_name(widget_text)
        widget_id = var_name.replace("checkbox_", "")
        
        text = CodeParser._extract_property_value(widget_text, "text")
        width = CodeParser._extract_property_value(widget_text, "width", 200)
        height = CodeParser._extract_property_value(widget_text, "height", 30)
        
        x, y = 0, 0
        if place_line:
            x, y = CodeParser._extract_position(place_line)
        
        properties = {
            'text': WidgetProperty('text', text or 'Checkbox', 'str'),
            'width': WidgetProperty('width', width, 'int'),
            'height': WidgetProperty('height', height, 'int')
        }
        
        return WidgetData(
            id=widget_id,
            type=WidgetType.CHECKBOX,
            x=x, y=y, width=width, height=height,
            properties=properties
        )
    
    @staticmethod
    def _parse_combobox_block(widget_text: str, place_line: str = None) -> WidgetData:
        """Parse combobox widget from complete widget block"""
        var_name = CodeParser._extract_variable_name(widget_text)
        widget_id = var_name.replace("combobox_", "")
        
        values = CodeParser._extract_property_value(widget_text, "values")
        width = CodeParser._extract_property_value(widget_text, "width", 200)
        height = CodeParser._extract_property_value(widget_text, "height", 30)
        
        x, y = 0, 0
        if place_line:
            x, y = CodeParser._extract_position(place_line)
        
        # Parse values list
        values_list = []
        if values and values.startswith('[') and values.endswith(']'):
            values_str = values[1:-1]  # Remove brackets
            values_list = [v.strip().strip("'\"") for v in values_str.split(',')]
        
        properties = {
            'values': WidgetProperty('values', values_list, 'list'),
            'width': WidgetProperty('width', width, 'int'),
            'height': WidgetProperty('height', height, 'int')
        }
        
        return WidgetData(
            id=widget_id,
            type=WidgetType.COMBOBOX,
            x=x, y=y, width=width, height=height,
            properties=properties
        )
    
    @staticmethod
    def _parse_slider_block(widget_text: str, place_line: str = None) -> WidgetData:
        """Parse slider widget from complete widget block"""
        var_name = CodeParser._extract_variable_name(widget_text)
        widget_id = var_name.replace("slider_", "")
        
        from_val = CodeParser._extract_property_value(widget_text, "from_", 0)
        to_val = CodeParser._extract_property_value(widget_text, "to", 100)
        width = CodeParser._extract_property_value(widget_text, "width", 200)
        height = CodeParser._extract_property_value(widget_text, "height", 20)
        
        x, y = 0, 0
        if place_line:
            x, y = CodeParser._extract_position(place_line)
        
        properties = {
            'from_': WidgetProperty('from_', from_val, 'int'),
            'to': WidgetProperty('to', to_val, 'int'),
            'value': WidgetProperty('value', 50, 'int'),
            'width': WidgetProperty('width', width, 'int'),
            'height': WidgetProperty('height', height, 'int')
        }
        
        return WidgetData(
            id=widget_id,
            type=WidgetType.SLIDER,
            x=x, y=y, width=width, height=height,
            properties=properties
        )
    
    @staticmethod
    def _parse_progressbar_block(widget_text: str, place_line: str = None) -> WidgetData:
        """Parse progressbar widget from complete widget block"""
        var_name = CodeParser._extract_variable_name(widget_text)
        widget_id = var_name.replace("progressbar_", "")
        
        width = CodeParser._extract_property_value(widget_text, "width", 200)
        height = CodeParser._extract_property_value(widget_text, "height", 20)
        
        x, y = 0, 0
        if place_line:
            x, y = CodeParser._extract_position(place_line)
        
        properties = {
            'mode': WidgetProperty('mode', 'determinate', 'str'),
            'value': WidgetProperty('value', 50, 'int'),
            'width': WidgetProperty('width', width, 'int'),
            'height': WidgetProperty('height', height, 'int')
        }
        
        return WidgetData(
            id=widget_id,
            type=WidgetType.PROGRESSBAR,
            x=x, y=y, width=width, height=height,
            properties=properties
        )
    
    @staticmethod
    def _extract_variable_name(line: str) -> str:
        """Extract variable name from widget creation line"""
        try:
            # Find self.widget_type_xxx = pattern
            start = line.find("self.")
            if start == -1:
                return ""
            
            end = line.find(" =", start)
            if end == -1:
                return ""
            
            return line[start+5:end]  # Skip "self."
        except:
            return ""
    
    @staticmethod
    def _extract_property_value(line: str, prop_name: str, default=None):
        """Extract property value from widget creation line"""
        try:
            # Look for prop_name=value pattern
            pattern = f"{prop_name}="
            start = line.find(pattern)
            if start == -1:
                return default
            
            start += len(pattern)
            
            # Find the end of the value
            if line[start] == "'" or line[start] == '"':
                # String value
                quote = line[start]
                start += 1
                end = line.find(quote, start)
                if end == -1:
                    return default
                return line[start:end]
            else:
                # Numeric value
                end = start
                while end < len(line) and (line[end].isdigit() or line[end] == '.' or line[end] == '-'):
                    end += 1
                if end == start:
                    return default
                return int(line[start:end]) if '.' not in line[start:end] else float(line[start:end])
        except:
            return default
    
    @staticmethod
    def _extract_position(line: str) -> tuple[int, int]:
        """Extract x, y position from place() call"""
        try:
            # Look for .place(x=..., y=...) pattern
            x_start = line.find("x=")
            if x_start == -1:
                return 0, 0
            
            x_start += 2
            x_end = x_start
            while x_end < len(line) and (line[x_end].isdigit() or line[x_end] == '-'):
                x_end += 1
            
            y_start = line.find("y=")
            if y_start == -1:
                return 0, 0
            
            y_start += 2
            y_end = y_start
            while y_end < len(line) and (line[y_end].isdigit() or line[y_end] == '-'):
                y_end += 1
            
            x = int(line[x_start:x_end]) if x_start < x_end else 0
            y = int(line[y_start:y_end]) if y_start < y_end else 0
            
            return x, y
        except:
            return 0, 0
