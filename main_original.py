#!/usr/bin/env python3
"""
Professional Python Drag-and-Drop GUI Builder Application
A modern, intuitive interface builder for CustomTkinter applications.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser
import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class WidgetType(Enum):
    """Enumeration of supported widget types"""
    BUTTON = "Button"
    LABEL = "Label"
    ENTRY = "Entry"
    CHECKBOX = "Checkbox"
    COMBOBOX = "Combobox"
    SLIDER = "Slider"
    PROGRESSBAR = "Progressbar"

@dataclass
class WidgetProperty:
    """Represents a widget property"""
    name: str
    value: Any
    type: str  # 'str', 'int', 'bool', 'list', 'color'
    options: Optional[List[str]] = None

@dataclass
class WidgetData:
    """Represents a widget in the design canvas"""
    id: str
    type: WidgetType
    x: int
    y: int
    width: int
    height: int
    properties: Dict[str, WidgetProperty]
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type.value,
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'properties': {k: {'name': v.name, 'value': v.value, 'type': v.type, 'options': v.options} 
                          for k, v in self.properties.items()}
        }

@dataclass
class AppPreferences:
    """Application preferences data structure"""
    # Appearance
    appearance_mode: str = "dark"  # "light", "dark", "system"
    color_theme: str = "blue"  # "blue", "green", "dark-blue"
    custom_primary_color: str = "#1f538d"
    custom_secondary_color: str = "#14375e"
    custom_success_color: str = "#00C851"
    custom_warning_color: str = "#ffbb33"
    custom_error_color: str = "#ff4444"
    
    # Window Settings
    window_width: int = 1400
    window_height: int = 900
    window_x: int = 100
    window_y: int = 100
    remember_window_position: bool = True
    remember_window_size: bool = True
    auto_save_interval: int = 300  # seconds
    
    # Editor Settings
    font_family: str = "Consolas"
    font_size: int = 12
    tab_size: int = 4
    use_spaces_for_tabs: bool = True
    show_line_numbers: bool = True
    show_whitespace: bool = False
    word_wrap: bool = True
    syntax_highlighting: bool = True
    auto_indent: bool = True
    bracket_matching: bool = True
    
    # Canvas Settings
    grid_size: int = 20
    show_grid: bool = True
    snap_to_grid: bool = True
    grid_color: str = "#404040"
    canvas_background: str = "#2b2b2b"
    selection_color: str = "#0078d4"
    hover_color: str = "#404040"
    
    # Widget Defaults
    default_button_width: int = 100
    default_button_height: int = 32
    default_label_width: int = 100
    default_label_height: int = 24
    default_entry_width: int = 120
    default_entry_height: int = 28
    
    # Code Generation
    generate_comments: bool = True
    generate_docstrings: bool = True
    code_style: str = "pep8"  # "pep8", "black", "custom"
    include_imports: bool = True
    include_main_guard: bool = True
    auto_format_code: bool = True
    
    # File Operations
    default_save_location: str = ""
    auto_save: bool = True
    backup_files: bool = True
    max_recent_files: int = 10
    confirm_before_close: bool = True
    
    # Performance
    enable_animations: bool = True
    animation_speed: int = 200  # milliseconds
    max_undo_history: int = 50
    enable_auto_complete: bool = True
    enable_tooltips: bool = True
    
    # Advanced
    debug_mode: bool = False
    log_level: str = "INFO"  # "DEBUG", "INFO", "WARNING", "ERROR"
    enable_telemetry: bool = False
    check_updates: bool = True
    experimental_features: bool = False

class PreferencesManager:
    """Manages application preferences with persistence"""
    
    def __init__(self, config_file: str = "preferences.json"):
        self.config_file = config_file
        self.preferences = AppPreferences()
        self.load_preferences()
    
    def load_preferences(self):
        """Load preferences from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Update preferences with loaded data
                    for key, value in data.items():
                        if hasattr(self.preferences, key):
                            setattr(self.preferences, key, value)
        except Exception as e:
            print(f"Error loading preferences: {e}")
    
    def save_preferences(self):
        """Save preferences to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.preferences), f, indent=2)
        except Exception as e:
            print(f"Error saving preferences: {e}")
    
    def get(self, key: str, default=None):
        """Get a preference value"""
        return getattr(self.preferences, key, default)
    
    def set(self, key: str, value):
        """Set a preference value"""
        if hasattr(self.preferences, key):
            setattr(self.preferences, key, value)
            self.save_preferences()
    
    def reset_to_defaults(self):
        """Reset all preferences to default values"""
        self.preferences = AppPreferences()
        self.save_preferences()

class WidgetToolbox(ctk.CTkFrame):
    """Left panel containing draggable widgets"""
    
    def __init__(self, parent, on_widget_drag_start):
        super().__init__(parent)
        self.on_widget_drag_start = on_widget_drag_start
        self.dragging_widget = None
        self.setup_ui()
    
    def setup_ui(self):
        self.configure(width=200, height=600)
        self.pack_propagate(False)
        
        # Title
        title = ctk.CTkLabel(self, text="Widget Toolbox", font=ctk.CTkFont(size=16, weight="bold"))
        title.pack(pady=10)
        
        # Widget categories
        self.create_widget_category("Basic Widgets", [
            ("Button", WidgetType.BUTTON, "🔘"),
            ("Label", WidgetType.LABEL, "🏷️"),
            ("Entry", WidgetType.ENTRY, "📝"),
            ("Checkbox", WidgetType.CHECKBOX, "☑️"),
        ])
        
        self.create_widget_category("Advanced Widgets", [
            ("Combobox", WidgetType.COMBOBOX, "📋"),
            ("Slider", WidgetType.SLIDER, "🎚️"),
            ("Progressbar", WidgetType.PROGRESSBAR, "📊"),
        ])
    
    def create_widget_category(self, title, widgets):
        """Create a category section with widgets"""
        category_frame = ctk.CTkFrame(self)
        category_frame.pack(fill="x", padx=10, pady=5)
        
        # Category title
        cat_label = ctk.CTkLabel(category_frame, text=title, font=ctk.CTkFont(weight="bold"))
        cat_label.pack(pady=5)
        
        # Widget buttons
        for name, widget_type, icon in widgets:
            # Create a closure to capture the widget_type properly
            def make_click_handler(wt):
                return lambda: self.on_widget_click(wt)
            
            def make_drag_handler(wt):
                return lambda e: self.start_drag(e, wt)
            
            btn = ctk.CTkButton(
                category_frame,
                text=f"{icon} {name}",
                command=make_click_handler(widget_type),
                height=30,
                width=150
            )
            # Bind drag events
            btn.bind("<Button-1>", make_drag_handler(widget_type))
            btn.bind("<B1-Motion>", self.on_drag)
            btn.bind("<ButtonRelease-1>", self.end_drag)
            btn.pack(pady=2)
    
    def on_widget_click(self, widget_type: WidgetType):
        """Handle widget button click - add widget to canvas"""
        # Get the canvas reference from the main app
        main_app = self.winfo_toplevel()
        if hasattr(main_app, 'canvas'):
            # Check if canvas is being interacted with
            if getattr(main_app.canvas, 'canvas_interacting', False):
                return  # Don't add widget if canvas is being interacted with
            
            # Check if this is part of a drag operation - if so, don't add widget here
            # The end_drag method will handle it if it was a real drag
            if hasattr(self, 'dragging_widget') and self.dragging_widget:
                return  # Don't add widget if drag is in progress
            
            # Add widget at center of canvas
            canvas_width = main_app.canvas.winfo_width()
            canvas_height = main_app.canvas.winfo_height()
            x = max(50, canvas_width // 2 - 50)
            y = max(50, canvas_height // 2 - 15)
            main_app.canvas.add_widget(widget_type, x, y)
            # Clear any existing selection to prevent duplication
            main_app.canvas.deselect_all()
            # Reset interaction flag
            main_app.canvas.canvas_interacting = False
    
    def start_drag(self, event, widget_type):
        """Start drag operation"""
        self.dragging_widget = widget_type
        self.drag_start_x = event.x_root
        self.drag_start_y = event.y_root
    
    def on_drag(self, event):
        """Handle drag motion"""
        if self.dragging_widget:
            # Visual feedback could be added here
            pass
    
    def end_drag(self, event):
        """End drag operation"""
        if self.dragging_widget:
            # Only add widget if this was actually a drag operation (not just a click)
            # Check if mouse moved significantly from start position
            if (hasattr(self, 'drag_start_x') and hasattr(self, 'drag_start_y') and
                abs(event.x_root - self.drag_start_x) > 5 and 
                abs(event.y_root - self.drag_start_y) > 5):
                # This was a real drag operation
                main_app = self.winfo_toplevel()
                if hasattr(main_app, 'canvas'):
                    canvas_width = main_app.canvas.winfo_width()
                    canvas_height = main_app.canvas.winfo_height()
                    x = max(50, canvas_width // 2 - 50)
                    y = max(50, canvas_height // 2 - 15)
                    main_app.canvas.add_widget(self.dragging_widget, x, y)
            self.dragging_widget = None

class DesignCanvas(ctk.CTkCanvas):
    """Center panel for designing the GUI"""
    
    def __init__(self, parent, on_widget_select, status_bar=None):
        super().__init__(parent, bg="#2b2b2b", highlightthickness=0)
        self.on_widget_select = on_widget_select
        self.status_bar = status_bar
        self.widgets: Dict[str, WidgetData] = {}
        self.selected_widget_id: Optional[str] = None
        self.drag_data = {"x": 0, "y": 0, "widget": None}
        self.grid_size = 10  # Smaller grid for smoother movement
        self.show_grid = True
        self.snap_to_grid = True  # Allow disabling grid snapping
        self.last_render_time = 0
        self.render_throttle = 16  # ~60 FPS
        self.canvas_interacting = False
        self.render_queue = []  # Queue for batched rendering
        self.render_scheduled = False  # Prevent multiple render schedules
        self.window_boundary_visible = True  # Show window boundary by default
        
        # Clipboard and undo/redo functionality
        self.clipboard = None
        self.undo_stack = []
        self.redo_stack = []
        self.max_undo_steps = 50
        
        self.setup_bindings()
        self.draw_grid()
    
    def setup_bindings(self):
        """Setup mouse event bindings"""
        self.bind("<Button-1>", self.on_canvas_click)
        self.bind("<B1-Motion>", self.on_canvas_drag)
        self.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.bind("<Button-3>", self.on_right_click)
        
        # Keyboard shortcuts
        self.bind("<KeyPress-Delete>", self.on_delete_key)
        self.bind("<KeyPress-BackSpace>", self.on_delete_key)
        self.bind("<Control-c>", self.on_copy)
        self.bind("<Control-v>", self.on_paste)
        self.bind("<Control-x>", self.on_cut)
        self.bind("<Control-z>", self.on_undo)
        self.bind("<Control-y>", self.on_redo)
        self.bind("<Control-a>", self.on_select_all)
        self.bind("<Control-d>", self.on_duplicate)
        self.bind("<Control-s>", self.on_save)
        self.bind("<Control-n>", self.on_new)
        self.bind("<Control-o>", self.on_open)
        self.bind("<F5>", self.on_preview)
        self.bind("<Escape>", self.on_escape)
        
        # Prevent focus issues
        self.bind("<FocusIn>", lambda e: None)
        self.bind("<FocusOut>", lambda e: None)
        self.focus_set()
    
    def draw_grid(self):
        """Draw grid lines on canvas"""
        if not self.show_grid:
            return
            
        self.delete("grid")
        width = self.winfo_width()
        height = self.winfo_height()
        
        if width <= 1 or height <= 1:  # Canvas not ready
            return
        
        # Draw vertical lines
        for x in range(0, width, self.grid_size):
            self.create_line(x, 0, x, height, fill="#404040", width=1, tags="grid")
        
        # Draw horizontal lines
        for y in range(0, height, self.grid_size):
            self.create_line(0, y, width, y, fill="#404040", width=1, tags="grid")
    
    def draw_window_boundary(self):
        """Draw the window boundary to show actual window size"""
        if not self.window_boundary_visible:
            return
        
        # Get window properties from main app
        main_app = self.winfo_toplevel()
        if not hasattr(main_app, 'window_properties'):
            return
        
        window_props = main_app.window_properties
        
        # Calculate actual window size (considering auto-fit)
        if window_props.get('auto_fit', True) and self.widgets:
            max_x = max(widget.x + widget.width for widget in self.widgets.values()) + 50
            max_y = max(widget.y + widget.height for widget in self.widgets.values()) + 50
            window_width = max(window_props['width'], max_x)
            window_height = max(window_props['height'], max_y)
        else:
            window_width = window_props['width']
            window_height = window_props['height']
        
        # Remove existing boundary
        self.delete("window_boundary")
        
        # Draw window boundary rectangle
        self.create_rectangle(
            0, 0, window_width, window_height,
            outline="#ff6b6b",  # Red outline
            width=3,
            dash=(5, 5),  # Dashed line
            tags="window_boundary"
        )
        
        # Add corner markers
        corner_size = 10
        corners = [
            (0, 0),  # Top-left
            (window_width, 0),  # Top-right
            (0, window_height),  # Bottom-left
            (window_width, window_height)  # Bottom-right
        ]
        
        for x, y in corners:
            self.create_rectangle(
                x - corner_size//2, y - corner_size//2,
                x + corner_size//2, y + corner_size//2,
                fill="#ff6b6b",
                outline="#ffffff",
                width=2,
                tags="window_boundary"
            )
        
        # Add size label
        label_text = f"Window: {window_width}×{window_height}"
        self.create_text(
            window_width//2, 20,
            text=label_text,
            fill="#ff6b6b",
            font=("Arial", 12, "bold"),
            tags="window_boundary"
        )
        
        # Add warning for widgets outside boundary
        self.check_widgets_outside_boundary(window_width, window_height)
    
    def check_widgets_outside_boundary(self, window_width: int, window_height: int):
        """Check for widgets outside the window boundary and show warnings"""
        # Remove existing warnings
        self.delete("boundary_warning")
        
        outside_widgets = []
        for widget_id, widget_data in self.widgets.items():
            if (widget_data.x < 0 or widget_data.y < 0 or 
                widget_data.x + widget_data.width > window_width or 
                widget_data.y + widget_data.height > window_height):
                outside_widgets.append(widget_data)
        
        if outside_widgets:
            # Show warning message
            warning_text = f"⚠️ {len(outside_widgets)} widget(s) outside window boundary!"
            self.create_text(
                window_width//2, window_height + 30,
                text=warning_text,
                fill="#ff4444",
                font=("Arial", 14, "bold"),
                tags="boundary_warning"
            )
            
            # Highlight problematic widgets
            for widget_data in outside_widgets:
                self.create_rectangle(
                    widget_data.x - 2, widget_data.y - 2,
                    widget_data.x + widget_data.width + 2, 
                    widget_data.y + widget_data.height + 2,
                    outline="#ff4444",
                    width=3,
                    dash=(3, 3),
                    tags="boundary_warning"
                )
    
    def add_widget(self, widget_type: WidgetType, x: int, y: int):
        """Add a new widget to the canvas"""
        widget_id = str(uuid.uuid4())
        
        # Default properties for each widget type
        default_properties = self.get_default_properties(widget_type)
        
        widget_data = WidgetData(
            id=widget_id,
            type=widget_type,
            x=x,
            y=y,
            width=100,
            height=30,
            properties=default_properties
        )
        
        self.widgets[widget_id] = widget_data
        self.render_widget(widget_data)
        self.select_widget(widget_id)
        # Ensure canvas has focus for keyboard events
        self.focus_set()
        
        # Mark project as modified
        main_app = self.winfo_toplevel()
        if hasattr(main_app, 'project_modified'):
            main_app.project_modified = True
            main_app.update_status_info()
    
    def get_default_properties(self, widget_type: WidgetType) -> Dict[str, WidgetProperty]:
        """Get default properties for a widget type"""
        properties = {}
        
        if widget_type == WidgetType.BUTTON:
            properties = {
                "text": WidgetProperty("text", "Button", "str"),
                "width": WidgetProperty("width", 100, "int"),
                "height": WidgetProperty("height", 30, "int"),
                "command": WidgetProperty("command", "", "str"),
            }
        elif widget_type == WidgetType.LABEL:
            properties = {
                "text": WidgetProperty("text", "Label", "str"),
                "width": WidgetProperty("width", 100, "int"),
                "height": WidgetProperty("height", 30, "int"),
                "font_size": WidgetProperty("font_size", 12, "int"),
            }
        elif widget_type == WidgetType.ENTRY:
            properties = {
                "placeholder": WidgetProperty("placeholder", "Enter text...", "str"),
                "width": WidgetProperty("width", 100, "int"),
                "height": WidgetProperty("height", 30, "int"),
            }
        elif widget_type == WidgetType.CHECKBOX:
            properties = {
                "text": WidgetProperty("text", "Checkbox", "str"),
                "checked": WidgetProperty("checked", False, "bool"),
                "width": WidgetProperty("width", 100, "int"),
                "height": WidgetProperty("height", 30, "int"),
            }
        elif widget_type == WidgetType.COMBOBOX:
            properties = {
                "values": WidgetProperty("values", "Option 1,Option 2,Option 3", "str"),
                "width": WidgetProperty("width", 100, "int"),
                "height": WidgetProperty("height", 30, "int"),
            }
        elif widget_type == WidgetType.SLIDER:
            properties = {
                "from_": WidgetProperty("from_", 0, "int"),
                "to": WidgetProperty("to", 100, "int"),
                "value": WidgetProperty("value", 50, "int"),
                "width": WidgetProperty("width", 200, "int"),
                "height": WidgetProperty("height", 20, "int"),
            }
        elif widget_type == WidgetType.PROGRESSBAR:
            properties = {
                "mode": WidgetProperty("mode", "determinate", "list", ["determinate", "indeterminate"]),
                "value": WidgetProperty("value", 50, "int"),
                "width": WidgetProperty("width", 200, "int"),
                "height": WidgetProperty("height", 20, "int"),
            }
        
        return properties
    
    def render_widget(self, widget_data: WidgetData):
        """Render a widget on the canvas with performance optimization"""
        # Add to render queue for batched processing
        if widget_data.id not in self.render_queue:
            self.render_queue.append(widget_data.id)
        
        # Schedule batched render if not already scheduled
        if not self.render_scheduled:
            self.render_scheduled = True
            self.after_idle(self.batched_render)
    
    def batched_render(self):
        """Render all queued widgets in a single batch"""
        self.render_scheduled = False
        
        # Process all queued widgets
        for widget_id in self.render_queue:
            if widget_id in self.widgets:
                self.render_single_widget(self.widgets[widget_id])
        
        # Clear the queue
        self.render_queue.clear()
        
        # Draw window boundary after rendering widgets
        self.draw_window_boundary()
    
    def render_single_widget(self, widget_data: WidgetData):
        """Render a single widget on the canvas"""
        # Remove existing widget representation and handles
        self.delete(f"widget_{widget_data.id}")
        self.delete(f"handle_{widget_data.id}")
        
        # Create widget representation
        x, y = widget_data.x, widget_data.y
        w, h = widget_data.width, widget_data.height
        
        # Get widget-specific colors and styling
        widget_colors = self.get_widget_colors(widget_data)
        
        # Main widget rectangle
        fill_color = widget_colors["fill"]
        outline_color = widget_colors["outline"]
        if widget_data.id == self.selected_widget_id:
            fill_color = "#0066cc"
            outline_color = "#ffffff"
        
        rect = self.create_rectangle(
            x, y, x + w, y + h,
            fill=fill_color,
            outline=outline_color,
            width=2,
            tags=f"widget_{widget_data.id}"
        )
        
        # Add widget-specific visual elements
        self.add_widget_specific_elements(widget_data, x, y, w, h)
        
        # Widget label
        label_text = self.get_widget_display_text(widget_data)
        self.create_text(
            x + w//2, y + h//2,
            text=label_text,
            fill="white",
            font=("Arial", 10),
            tags=f"widget_{widget_data.id}"
        )
        
        # Selection handles (only for selected widget)
        if widget_data.id == self.selected_widget_id:
            self.draw_selection_handles(widget_data)
    
    def get_widget_display_text(self, widget_data: WidgetData) -> str:
        """Get display text for widget"""
        # Use string comparison to be more reliable
        widget_type_str = widget_data.type.value
        
        if widget_type_str == "Button":
            return widget_data.properties["text"].value
        elif widget_type_str == "Label":
            return widget_data.properties["text"].value
        elif widget_type_str == "Entry":
            return widget_data.properties["placeholder"].value
        elif widget_type_str == "Checkbox":
            return widget_data.properties["text"].value
        elif widget_type_str == "Combobox":
            return "Combobox"
        elif widget_type_str == "Slider":
            return f"Slider ({widget_data.properties['value'].value})"
        elif widget_type_str == "Progressbar":
            return f"Progress ({widget_data.properties['value'].value}%)"
        
        return widget_data.type.value
    
    def get_widget_colors(self, widget_data: WidgetData) -> Dict[str, str]:
        """Get widget-specific colors"""
        widget_type_str = widget_data.type.value
        
        if widget_type_str == "Button":
            return {"fill": "#2d5a27", "outline": "#4a7c59"}  # Green tones
        elif widget_type_str == "Label":
            return {"fill": "#2b2b2b", "outline": "#666666"}  # Dark gray
        elif widget_type_str == "Entry":
            return {"fill": "#1a1a1a", "outline": "#555555"}  # Very dark
        elif widget_type_str == "Checkbox":
            return {"fill": "#3d2d5a", "outline": "#6a4c93"}  # Purple tones
        elif widget_type_str == "Combobox":
            return {"fill": "#2d4a5a", "outline": "#4a7c8a"}  # Blue-gray
        elif widget_type_str == "Slider":
            return {"fill": "#5a2d2d", "outline": "#8a4a4a"}  # Red tones
        elif widget_type_str == "Progressbar":
            return {"fill": "#2d5a2d", "outline": "#4a7c4a"}  # Green tones
        else:
            return {"fill": "#4a4a4a", "outline": "#666666"}  # Default gray
    
    def add_widget_specific_elements(self, widget_data: WidgetData, x: int, y: int, w: int, h: int):
        """Add widget-specific visual elements"""
        widget_type_str = widget_data.type.value
        
        if widget_type_str == "Button":
            # Add a subtle 3D effect for buttons
            self.create_line(x+1, y+1, x+w-1, y+1, fill="#ffffff", width=1, tags=f"widget_{widget_data.id}")
            self.create_line(x+1, y+1, x+1, y+h-1, fill="#ffffff", width=1, tags=f"widget_{widget_data.id}")
            self.create_line(x+w-1, y+1, x+w-1, y+h-1, fill="#000000", width=1, tags=f"widget_{widget_data.id}")
            self.create_line(x+1, y+h-1, x+w-1, y+h-1, fill="#000000", width=1, tags=f"widget_{widget_data.id}")
            
        elif widget_type_str == "Entry":
            # Add a subtle border effect for entry fields
            self.create_rectangle(x+2, y+2, x+w-2, y+h-2, outline="#888888", width=1, fill="", tags=f"widget_{widget_data.id}")
            
        elif widget_type_str == "Checkbox":
            # Add a small square for checkbox
            checkbox_size = min(12, h-4)
            checkbox_x = x + 4
            checkbox_y = y + (h - checkbox_size) // 2
            self.create_rectangle(checkbox_x, checkbox_y, checkbox_x + checkbox_size, checkbox_y + checkbox_size, 
                                fill="#ffffff", outline="#000000", width=1, tags=f"widget_{widget_data.id}")
            
        elif widget_type_str == "Combobox":
            # Add a dropdown arrow
            arrow_size = 6
            arrow_x = x + w - 12
            arrow_y = y + h // 2
            self.create_polygon(arrow_x, arrow_y - arrow_size//2, 
                               arrow_x + arrow_size, arrow_y - arrow_size//2,
                               arrow_x + arrow_size//2, arrow_y + arrow_size//2,
                               fill="#ffffff", outline="#000000", width=1, tags=f"widget_{widget_data.id}")
            
        elif widget_type_str == "Slider":
            # Add a track line and thumb
            track_y = y + h // 2
            self.create_line(x + 5, track_y, x + w - 5, track_y, fill="#666666", width=2, tags=f"widget_{widget_data.id}")
            # Thumb position based on value
            value = widget_data.properties.get("value", WidgetProperty("value", 50, "int")).value
            from_val = widget_data.properties.get("from_", WidgetProperty("from_", 0, "int")).value
            to_val = widget_data.properties.get("to", WidgetProperty("to", 100, "int")).value
            if to_val > from_val:
                thumb_x = x + 5 + int((value - from_val) / (to_val - from_val) * (w - 10))
                self.create_oval(thumb_x - 4, track_y - 4, thumb_x + 4, track_y + 4, 
                                fill="#ffffff", outline="#000000", width=1, tags=f"widget_{widget_data.id}")
            
        elif widget_type_str == "Progressbar":
            # Add progress fill
            value = widget_data.properties.get("value", WidgetProperty("value", 50, "int")).value
            fill_width = int((value / 100) * (w - 4))
            if fill_width > 0:
                self.create_rectangle(x + 2, y + 2, x + 2 + fill_width, y + h - 2, 
                                    fill="#4CAF50", outline="", tags=f"widget_{widget_data.id}")
    
    def draw_selection_handles(self, widget_data: WidgetData):
        """Draw resize handles for selected widget"""
        x, y = widget_data.x, widget_data.y
        w, h = widget_data.width, widget_data.height
        handle_size = 8
        
        # Corner handles only
        handles = [
            (x - handle_size//2, y - handle_size//2),  # Top-left
            (x + w - handle_size//2, y - handle_size//2),  # Top-right
            (x - handle_size//2, y + h - handle_size//2),  # Bottom-left
            (x + w - handle_size//2, y + h - handle_size//2),  # Bottom-right
        ]
        
        for i, (hx, hy) in enumerate(handles):
            self.create_rectangle(
                hx, hy, hx + handle_size, hy + handle_size,
                fill="#0066cc",
                outline="#ffffff",
                width=2,
                tags=f"handle_{widget_data.id}"
            )
    
    def on_canvas_click(self, event):
        """Handle canvas click events"""
        self.canvas_interacting = True
        # Ensure canvas has focus for keyboard events
        self.focus_set()
        
        # First check if clicking on a resize handle
        handle_info = self.find_handle_at_position(event.x, event.y)
        if handle_info:
            widget_id, handle_index = handle_info
            self.select_widget(widget_id)
            widget_data = self.widgets[widget_id]
            # Set resize data with original dimensions
            self.drag_data = {
                "x": event.x, 
                "y": event.y, 
                "widget": widget_id, 
                "mode": "resize", 
                "handle": handle_index,
                "original_x": widget_data.x,
                "original_y": widget_data.y,
                "original_width": widget_data.width,
                "original_height": widget_data.height
            }
            return "break"
        
        # Then check if clicking on a widget
        widget_id = self.find_widget_at_position(event.x, event.y)
        if widget_id:
            self.select_widget(widget_id)
            widget_data = self.widgets[widget_id]
            # Set drag data for potential dragging with proper offset calculation
            self.drag_data = {
                "x": event.x, 
                "y": event.y, 
                "widget": widget_id, 
                "mode": "move",
                "original_x": widget_data.x,
                "original_y": widget_data.y,
                "click_offset_x": event.x - widget_data.x,
                "click_offset_y": event.y - widget_data.y
            }
            # Stop event propagation to prevent toolbox from responding
            return "break"
        else:
            self.deselect_all()
            # Clear drag data when clicking empty space
            self.drag_data = {"x": 0, "y": 0, "widget": None, "mode": None}
    
    def find_widget_at_position(self, x: int, y: int) -> Optional[str]:
        """Find widget at given position"""
        for widget_id, widget_data in self.widgets.items():
            if (widget_data.x <= x <= widget_data.x + widget_data.width and
                widget_data.y <= y <= widget_data.y + widget_data.height):
                return widget_id
        return None
    
    def find_handle_at_position(self, x: int, y: int) -> Optional[tuple]:
        """Find resize handle at given position. Returns (widget_id, handle_index) or None"""
        if not self.selected_widget_id:
            return None
            
        widget_data = self.widgets[self.selected_widget_id]
        handle_size = 8
        x_pos, y_pos = widget_data.x, widget_data.y
        w, h = widget_data.width, widget_data.height
        
        # Check each handle
        handles = [
            (x_pos - handle_size//2, y_pos - handle_size//2),  # Top-left
            (x_pos + w - handle_size//2, y_pos - handle_size//2),  # Top-right
            (x_pos - handle_size//2, y_pos + h - handle_size//2),  # Bottom-left
            (x_pos + w - handle_size//2, y_pos + h - handle_size//2),  # Bottom-right
        ]
        
        for i, (hx, hy) in enumerate(handles):
            if (hx <= x <= hx + handle_size and hy <= y <= hy + handle_size):
                return (self.selected_widget_id, i)
        return None
    
    
    def select_widget(self, widget_id: str):
        """Select a widget"""
        self.selected_widget_id = widget_id
        self.on_widget_select(self.widgets[widget_id])
        self.render_widget(self.widgets[widget_id])
    
    def deselect_all(self):
        """Deselect all widgets"""
        self.selected_widget_id = None
        self.on_widget_select(None)
        for widget_data in self.widgets.values():
            self.render_widget(widget_data)
    
    def on_canvas_drag(self, event):
        """Handle canvas drag events"""
        if self.drag_data["widget"]:
            widget_id = self.drag_data["widget"]
            widget_data = self.widgets[widget_id]
            mode = self.drag_data.get("mode", "move")
            
            if mode == "move":
                # Handle widget moving - use absolute positioning for smoother movement
                # Calculate new position relative to the original click position
                original_x = self.drag_data.get("original_x", widget_data.x)
                original_y = self.drag_data.get("original_y", widget_data.y)
                click_offset_x = self.drag_data.get("click_offset_x", 0)
                click_offset_y = self.drag_data.get("click_offset_y", 0)
                
                new_x = event.x - click_offset_x
                new_y = event.y - click_offset_y
                
                # Snap to grid if enabled
                if self.snap_to_grid:
                    new_x = round(new_x / self.grid_size) * self.grid_size
                    new_y = round(new_y / self.grid_size) * self.grid_size
                
                # Update widget position
                widget_data.x = max(0, new_x)
                widget_data.y = max(0, new_y)
                
                # Re-render the widget completely to avoid artifacts
                self.render_widget(widget_data)
                
            elif mode == "resize":
                # Handle widget resizing with smooth absolute positioning
                handle_index = self.drag_data["handle"]
                
                # Get original widget dimensions and position
                original_x = self.drag_data.get("original_x", widget_data.x)
                original_y = self.drag_data.get("original_y", widget_data.y)
                original_width = self.drag_data.get("original_width", widget_data.width)
                original_height = self.drag_data.get("original_height", widget_data.height)
                
                # Calculate new dimensions based on handle and current mouse position
                new_x, new_y = original_x, original_y
                new_width, new_height = original_width, original_height
                
                if handle_index == 0:  # Top-left
                    new_x = event.x
                    new_y = event.y
                    new_width = original_width + (original_x - event.x)
                    new_height = original_height + (original_y - event.y)
                elif handle_index == 1:  # Top-right
                    new_y = event.y
                    new_width = event.x - original_x
                    new_height = original_height + (original_y - event.y)
                elif handle_index == 2:  # Bottom-left
                    new_x = event.x
                    new_width = original_width + (original_x - event.x)
                    new_height = event.y - original_y
                elif handle_index == 3:  # Bottom-right
                    new_width = event.x - original_x
                    new_height = event.y - original_y
                
                # Apply minimum size constraints
                new_width = max(20, new_width)
                new_height = max(20, new_height)
                
                # Snap to grid if enabled
                if self.snap_to_grid:
                    new_x = round(new_x / self.grid_size) * self.grid_size
                    new_y = round(new_y / self.grid_size) * self.grid_size
                    new_width = round(new_width / self.grid_size) * self.grid_size
                    new_height = round(new_height / self.grid_size) * self.grid_size
                
                # Update widget properties
                widget_data.x = max(0, new_x)
                widget_data.y = max(0, new_y)
                widget_data.width = new_width
                widget_data.height = new_height
                
                # Update the properties dictionary to reflect the changes
                if "width" in widget_data.properties:
                    widget_data.properties["width"].value = new_width
                if "height" in widget_data.properties:
                    widget_data.properties["height"].value = new_height
                
                # Update properties in the properties editor
                main_app = self.winfo_toplevel()
                if hasattr(main_app, 'properties_editor'):
                    main_app.properties_editor.set_widget(widget_data)
                
                # Re-render the widget with new dimensions
                self.render_widget(widget_data)
    
    
    def on_canvas_release(self, event):
        """Handle canvas release events"""
        self.drag_data = {"x": 0, "y": 0, "widget": None, "mode": None}
        # Reset the interaction flag after a short delay
        self.after(100, lambda: setattr(self, 'canvas_interacting', False))
    
    def on_right_click(self, event):
        """Handle right-click context menu"""
        widget_id = self.find_widget_at_position(event.x, event.y)
        if widget_id:
            self.show_context_menu(event.x, event.y, widget_id)
    
    def show_context_menu(self, x: int, y: int, widget_id: str):
        """Show context menu for widget"""
        context_menu = tk.Menu(self, tearoff=0)
        context_menu.add_command(label="Delete", command=lambda: self.delete_widget(widget_id))
        context_menu.add_command(label="Duplicate", command=lambda: self.duplicate_widget(widget_id))
        context_menu.add_command(label="Bring to Front", command=lambda: self.bring_to_front(widget_id))
        context_menu.add_command(label="Send to Back", command=lambda: self.send_to_back(widget_id))
        
        try:
            context_menu.tk_popup(x, y)
        finally:
            context_menu.grab_release()
    
    def delete_widget(self, widget_id: str):
        """Delete a widget"""
        if widget_id in self.widgets:
            del self.widgets[widget_id]
            self.delete(f"widget_{widget_id}")
            self.delete(f"handle_{widget_id}")
            if self.selected_widget_id == widget_id:
                self.deselect_all()
            
            # Mark project as modified
            main_app = self.winfo_toplevel()
            if hasattr(main_app, 'project_modified'):
                main_app.project_modified = True
                main_app.update_status_info()
    
    def duplicate_widget(self, widget_id: str):
        """Duplicate a widget"""
        if widget_id in self.widgets:
            original = self.widgets[widget_id]
            new_widget = WidgetData(
                id=str(uuid.uuid4()),
                type=original.type,
                x=original.x + 20,
                y=original.y + 20,
                width=original.width,
                height=original.height,
                properties=original.properties.copy()
            )
            self.widgets[new_widget.id] = new_widget
            self.render_widget(new_widget)
    
    def bring_to_front(self, widget_id: str):
        """Bring widget to front"""
        if widget_id in self.widgets:
            # Re-render to bring to front
            self.render_widget(self.widgets[widget_id])
    
    def send_to_back(self, widget_id: str):
        """Send widget to back"""
        if widget_id in self.widgets:
            # Re-render all widgets to send to back
            for wd in self.widgets.values():
                self.render_widget(wd)
    
    def on_delete_key(self, event):
        """Handle delete key press"""
        if self.selected_widget_id:
            self.save_state()  # Save state before deletion
            self.delete_widget(self.selected_widget_id)
            if self.status_bar:
                self.status_bar.configure(text="Widget deleted")
        return "break"
    
    def on_copy(self, event):
        """Copy selected widget to clipboard"""
        if self.selected_widget_id:
            widget_data = self.widgets[self.selected_widget_id]
            self.clipboard = widget_data
            if self.status_bar:
                self.status_bar.configure(text="Widget copied to clipboard")
        return "break"
    
    def on_cut(self, event):
        """Cut selected widget to clipboard"""
        if self.selected_widget_id:
            widget_data = self.widgets[self.selected_widget_id]
            self.clipboard = widget_data
            self.save_state()  # Save state before deletion
            self.delete_widget(self.selected_widget_id)
            if self.status_bar:
                self.status_bar.configure(text="Widget cut to clipboard")
        return "break"
    
    def on_paste(self, event):
        """Paste widget from clipboard"""
        if self.clipboard:
            # Create a new widget based on clipboard
            new_widget = WidgetData(
                id=str(uuid.uuid4()),
                type=self.clipboard.type,
                x=self.clipboard.x + 20,  # Offset slightly
                y=self.clipboard.y + 20,
                width=self.clipboard.width,
                height=self.clipboard.height,
                properties=self.clipboard.properties.copy()
            )
            self.save_state()  # Save state before adding
            self.widgets[new_widget.id] = new_widget
            self.render_widget(new_widget)
            self.select_widget(new_widget.id)
            if self.status_bar:
                self.status_bar.configure(text="Widget pasted from clipboard")
        return "break"
    
    def on_duplicate(self, event):
        """Duplicate selected widget"""
        if self.selected_widget_id:
            self.save_state()  # Save state before duplication
            self.duplicate_widget(self.selected_widget_id)
            if self.status_bar:
                self.status_bar.configure(text="Widget duplicated")
        return "break"
    
    def on_select_all(self, event):
        """Select all widgets"""
        if self.widgets:
            # For now, just select the first widget
            # In a full implementation, you'd select all widgets
            first_widget_id = list(self.widgets.keys())[0]
            self.select_widget(first_widget_id)
            if self.status_bar:
                self.status_bar.configure(text="Widget selected")
        return "break"
    
    def on_undo(self, event):
        """Undo last action"""
        if self.undo_stack:
            self.save_state_to_redo()
            state = self.undo_stack.pop()
            self.restore_state(state)
            if self.status_bar:
                self.status_bar.configure(text="Action undone")
        return "break"
    
    def on_redo(self, event):
        """Redo last undone action"""
        if self.redo_stack:
            self.save_state_to_undo()
            state = self.redo_stack.pop()
            self.restore_state(state)
            if self.status_bar:
                self.status_bar.configure(text="Action redone")
        return "break"
    
    def on_save(self, event):
        """Save project"""
        main_app = self.winfo_toplevel()
        if hasattr(main_app, 'save_project'):
            main_app.save_project()
            if self.status_bar:
                self.status_bar.configure(text="Project saved")
        return "break"
    
    def on_new(self, event):
        """New project"""
        main_app = self.winfo_toplevel()
        if hasattr(main_app, 'new_project'):
            main_app.new_project()
            if self.status_bar:
                self.status_bar.configure(text="New project created")
        return "break"
    
    def on_open(self, event):
        """Open project"""
        main_app = self.winfo_toplevel()
        if hasattr(main_app, 'open_project'):
            main_app.open_project()
            if self.status_bar:
                self.status_bar.configure(text="Project opened")
        return "break"
    
    def on_preview(self, event):
        """Preview GUI"""
        main_app = self.winfo_toplevel()
        if hasattr(main_app, 'preview_gui'):
            main_app.preview_gui()
            if self.status_bar:
                self.status_bar.configure(text="Preview opened")
        return "break"
    
    def on_escape(self, event):
        """Escape key - deselect all"""
        self.deselect_all()
        if self.status_bar:
            self.status_bar.configure(text="Selection cleared")
        return "break"
    
    def save_state(self):
        """Save current state for undo"""
        if len(self.undo_stack) >= self.max_undo_steps:
            self.undo_stack.pop(0)  # Remove oldest state
        
        state = {
            'widgets': {k: v.to_dict() for k, v in self.widgets.items()},
            'selected_widget_id': self.selected_widget_id
        }
        self.undo_stack.append(state)
        self.redo_stack.clear()  # Clear redo stack when new action is performed
    
    def save_state_to_undo(self):
        """Save current state to undo stack"""
        state = {
            'widgets': {k: v.to_dict() for k, v in self.widgets.items()},
            'selected_widget_id': self.selected_widget_id
        }
        self.undo_stack.append(state)
    
    def save_state_to_redo(self):
        """Save current state to redo stack"""
        state = {
            'widgets': {k: v.to_dict() for k, v in self.widgets.items()},
            'selected_widget_id': self.selected_widget_id
        }
        self.redo_stack.append(state)
    
    def restore_state(self, state):
        """Restore state from undo/redo stack"""
        # Clear current widgets
        self.widgets.clear()
        self.delete("all")
        
        # Restore widgets
        for widget_data in state['widgets'].values():
            widget = WidgetData(
                id=widget_data['id'],
                type=WidgetType(widget_data['type']),
                x=widget_data['x'],
                y=widget_data['y'],
                width=widget_data['width'],
                height=widget_data['height'],
                properties={
                    k: WidgetProperty(
                        name=v['name'],
                        value=v['value'],
                        type=v['type'],
                        options=v.get('options')
                    )
                    for k, v in widget_data['properties'].items()
                }
            )
            self.widgets[widget.id] = widget
            self.render_widget(widget)
        
        # Restore selection
        if state['selected_widget_id'] and state['selected_widget_id'] in self.widgets:
            self.select_widget(state['selected_widget_id'])
        else:
            self.deselect_all()
        
        self.draw_grid()
    
    def update_widget_property(self, widget_id: str, property_name: str, value: Any):
        """Update a widget property"""
        if widget_id in self.widgets:
            if property_name in self.widgets[widget_id].properties:
                self.widgets[widget_id].properties[property_name].value = value
                self.render_widget(self.widgets[widget_id])
                
                # Mark project as modified
                main_app = self.winfo_toplevel()
                if hasattr(main_app, 'project_modified'):
                    main_app.project_modified = True
                    main_app.update_status_info()
    
    def highlight_widgets_from_code(self, widget_ids: List[str]):
        """Highlight widgets that were updated from code"""
        try:
            # Clear previous highlights
            self.delete("code_update_highlight")
            
            # Highlight each widget with a temporary border
            for widget_id in widget_ids:
                if widget_id in self.widgets:
                    widget = self.widgets[widget_id]
                    
                    # Create a temporary highlight rectangle
                    highlight_id = self.create_rectangle(
                        widget.x - 2, widget.y - 2,
                        widget.x + widget.width + 2, widget.y + widget.height + 2,
                        outline="#00ff00", width=3, fill="", tags="code_update_highlight"
                    )
                    
                    # Remove highlight after 2 seconds
                    self.after(2000, lambda: self.delete("code_update_highlight"))
            
        except Exception as e:
            print(f"Error highlighting widgets: {e}")

class PropertiesEditor(ctk.CTkFrame):
    """Right panel for editing widget properties"""
    
    def __init__(self, parent, on_property_change):
        super().__init__(parent)
        self.on_property_change = on_property_change
        self.current_widget: Optional[WidgetData] = None
        self.property_widgets: Dict[str, ctk.CTkBaseClass] = {}
        
        self.setup_ui()
    
    def setup_ui(self):
        self.configure(width=250, height=600)
        self.pack_propagate(False)
        
        # Title
        title = ctk.CTkLabel(self, text="Properties", font=ctk.CTkFont(size=16, weight="bold"))
        title.pack(pady=10)
        
        # Properties frame
        self.properties_frame = ctk.CTkScrollableFrame(self)
        self.properties_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # No selection label
        self.no_selection_label = ctk.CTkLabel(
            self.properties_frame,
            text="Select a widget to edit its properties",
            font=ctk.CTkFont(size=12)
        )
        self.no_selection_label.pack(pady=20)
    
    def set_widget(self, widget_data: Optional[WidgetData]):
        """Set the current widget for editing"""
        self.current_widget = widget_data
        
        # Clear existing property widgets
        for widget in self.property_widgets.values():
            widget.destroy()
        self.property_widgets.clear()
        
        # Clear the properties frame completely
        for child in self.properties_frame.winfo_children():
            child.destroy()
        
        if widget_data is None:
            self.no_selection_label = ctk.CTkLabel(
                self.properties_frame,
                text="Select a widget to edit its properties",
                font=ctk.CTkFont(size=12)
            )
            self.no_selection_label.pack(pady=20)
            return
        
        # Create property editors
        for prop_name, prop in widget_data.properties.items():
            self.create_property_editor(prop_name, prop)
    
    def create_property_editor(self, prop_name: str, prop: WidgetProperty):
        """Create a property editor widget"""
        # Property label
        label = ctk.CTkLabel(
            self.properties_frame,
            text=prop.name.replace("_", " ").title(),
            font=ctk.CTkFont(weight="bold")
        )
        label.pack(pady=(10, 5), anchor="w")
        
        # Property editor based on type
        if prop.type == "str":
            editor = ctk.CTkEntry(
                self.properties_frame,
                placeholder_text=f"Enter {prop.name}",
                width=200
            )
            editor.insert(0, str(prop.value))
            editor.bind("<KeyRelease>", lambda e, pn=prop_name: self.on_property_change(pn, editor.get()))
            
        elif prop.type == "int":
            editor = ctk.CTkEntry(
                self.properties_frame,
                placeholder_text=f"Enter {prop.name}",
                width=200
            )
            editor.insert(0, str(prop.value))
            editor.bind("<KeyRelease>", lambda e, pn=prop_name: self.on_property_change(pn, int(editor.get()) if editor.get().isdigit() else 0))
            
        elif prop.type == "bool":
            editor = ctk.CTkCheckBox(
                self.properties_frame,
                text="",
                width=200
            )
            if prop.value:
                editor.select()
            editor.configure(command=lambda pn=prop_name: self.on_property_change(pn, editor.get()))
            
        elif prop.type == "list":
            editor = ctk.CTkComboBox(
                self.properties_frame,
                values=prop.options or [],
                width=200
            )
            editor.set(prop.value)
            editor.configure(command=lambda pn=prop_name: self.on_property_change(pn, editor.get()))
            
        else:
            editor = ctk.CTkEntry(
                self.properties_frame,
                placeholder_text=f"Enter {prop.name}",
                width=200
            )
            editor.insert(0, str(prop.value))
            editor.bind("<KeyRelease>", lambda e, pn=prop_name: self.on_property_change(pn, editor.get()))
        
        self.property_widgets[prop_name] = editor
        editor.pack(pady=2, anchor="w")

class CodeEditor(ctk.CTkFrame):
    """Code editor panel for editing generated Python code"""
    
    def __init__(self, parent, on_code_change):
        super().__init__(parent)
        self.on_code_change = on_code_change
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the code editor UI"""
        self.configure(width=400, height=600)
        self.pack_propagate(False)
        
        # Title
        title = ctk.CTkLabel(self, text="Code Editor", font=ctk.CTkFont(size=16, weight="bold"))
        title.pack(pady=10)
        
        # Code text area with scrollbar
        self.code_text = ctk.CTkTextbox(
            self,
            width=380,
            height=500,
            font=ctk.CTkFont(family="Consolas", size=11),
            wrap="none"
        )
        self.code_text.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Bind text change events
        self.code_text.bind("<KeyRelease>", self.on_text_change)
        self.code_text.bind("<Button-1>", self.on_text_change)
    
    def set_code(self, code: str):
        """Set the code content"""
        self.code_text.delete("1.0", "end")
        self.code_text.insert("1.0", code)
    
    def get_code(self) -> str:
        """Get the current code content"""
        return self.code_text.get("1.0", "end-1c")
    
    def on_text_change(self, event=None):
        """Handle text change events"""
        if self.on_code_change:
            self.on_code_change(self.get_code())
    
    def highlight_syntax(self):
        """Basic syntax highlighting (placeholder for future enhancement)"""
        # This could be enhanced with proper Python syntax highlighting
        pass

class PopOutCodeEditor(ctk.CTkToplevel):
    """Pop-out window for the code editor"""
    
    def __init__(self, parent_app, on_code_change, on_close_callback):
        super().__init__()
        self.parent_app = parent_app
        self.on_code_change = on_code_change
        self.on_close_callback = on_close_callback
        
        self.title("Code Editor - Pop-out")
        self.geometry("600x700")
        self.minsize(400, 300)
        
        # Make this window stay on top of the main window
        self.transient(parent_app)
        self.grab_set()
        
        # Setup the UI
        self.setup_ui()
        
        # Handle window close events
        self.protocol("WM_DELETE_WINDOW", self.on_window_close)
    
    def setup_ui(self):
        """Setup the pop-out code editor UI"""
        # Main frame
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title = ctk.CTkLabel(main_frame, text="Code Editor", font=ctk.CTkFont(size=16, weight="bold"))
        title.pack(pady=10)
        
        # Code text area with scrollbar
        self.code_text = ctk.CTkTextbox(
            main_frame,
            font=ctk.CTkFont(family="Consolas", size=11),
            wrap="none"
        )
        self.code_text.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Control buttons frame
        controls_frame = ctk.CTkFrame(main_frame)
        controls_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        # Control buttons
        self.sync_button = ctk.CTkButton(
            controls_frame, text="🔄 Sync from Design", width=120, height=25,
            command=self.sync_from_design, font=ctk.CTkFont(size=10)
        )
        self.sync_button.pack(side="left", padx=5, pady=5)
        
        self.validate_button = ctk.CTkButton(
            controls_frame, text="✅ Validate", width=80, height=25,
            command=self.validate_code, font=ctk.CTkFont(size=10)
        )
        self.validate_button.pack(side="left", padx=5, pady=5)
        
        self.run_button = ctk.CTkButton(
            controls_frame, text="▶️ Run Code", width=80, height=25,
            command=self.run_code, font=ctk.CTkFont(size=10)
        )
        self.run_button.pack(side="left", padx=5, pady=5)
        
        self.export_button = ctk.CTkButton(
            controls_frame, text="💾 Export", width=80, height=25,
            command=self.export_code, font=ctk.CTkFont(size=10)
        )
        self.export_button.pack(side="right", padx=5, pady=5)
        
        # Pop-in button
        self.pop_in_button = ctk.CTkButton(
            controls_frame, text="📌 Pop Back In", width=100, height=25,
            command=self.pop_back_in, font=ctk.CTkFont(size=10)
        )
        self.pop_in_button.pack(side="right", padx=5, pady=5)
        
        # Bind text change events
        self.code_text.bind("<KeyRelease>", self.on_text_change)
        self.code_text.bind("<Button-1>", self.on_text_change)
    
    def set_code(self, code: str):
        """Set the code content"""
        self.code_text.delete("1.0", "end")
        self.code_text.insert("1.0", code)
    
    def get_code(self) -> str:
        """Get the current code content"""
        return self.code_text.get("1.0", "end-1c")
    
    def on_text_change(self, event=None):
        """Handle text change events"""
        if self.on_code_change:
            self.on_code_change(self.get_code())
    
    def sync_from_design(self):
        """Sync code from the design canvas"""
        if hasattr(self.parent_app, 'sync_code_from_design'):
            self.parent_app.sync_code_from_design()
    
    def validate_code(self):
        """Validate the current code"""
        if hasattr(self.parent_app, 'validate_code'):
            self.parent_app.validate_code()
    
    def run_code(self):
        """Run the current code"""
        if hasattr(self.parent_app, 'run_generated_code'):
            self.parent_app.run_generated_code()
    
    def export_code(self):
        """Export the current code"""
        if hasattr(self.parent_app, 'export_edited_code'):
            self.parent_app.export_edited_code()
    
    def pop_back_in(self):
        """Pop the code editor back into the main window"""
        self.on_close_callback()
        self.destroy()
    
    def on_window_close(self):
        """Handle window close event"""
        self.on_close_callback()
        self.destroy()

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
    def _parse_widget_line(line: str) -> Optional[WidgetData]:
        """Parse a single widget creation line (legacy method)"""
        try:
            # Extract widget type and variable name
            if "self.button_" in line:
                return CodeParser._parse_button(line)
            elif "self.label_" in line:
                return CodeParser._parse_label(line)
            elif "self.entry_" in line:
                return CodeParser._parse_entry(line)
            elif "self.checkbox_" in line:
                return CodeParser._parse_checkbox(line)
            elif "self.combobox_" in line:
                return CodeParser._parse_combobox(line)
            elif "self.slider_" in line:
                return CodeParser._parse_slider(line)
            elif "self.progressbar_" in line:
                return CodeParser._parse_progressbar(line)
            
            return None
        except Exception as e:
            print(f"Error parsing widget line: {e}")
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
    def _parse_button(line: str) -> WidgetData:
        """Parse button widget from code (legacy method)"""
        # Extract variable name and properties
        var_name = CodeParser._extract_variable_name(line)
        widget_id = var_name.replace("button_", "")
        
        # Extract properties
        text = CodeParser._extract_property_value(line, "text")
        width = CodeParser._extract_property_value(line, "width", 100)
        height = CodeParser._extract_property_value(line, "height", 30)
        x, y = CodeParser._extract_position(line)
        
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
    def _parse_label(line: str) -> WidgetData:
        """Parse label widget from code"""
        var_name = CodeParser._extract_variable_name(line)
        widget_id = var_name.replace("label_", "")
        
        text = CodeParser._extract_property_value(line, "text")
        width = CodeParser._extract_property_value(line, "width", 200)
        height = CodeParser._extract_property_value(line, "height", 30)
        x, y = CodeParser._extract_position(line)
        
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
    def _parse_entry(line: str) -> WidgetData:
        """Parse entry widget from code"""
        var_name = CodeParser._extract_variable_name(line)
        widget_id = var_name.replace("entry_", "")
        
        placeholder = CodeParser._extract_property_value(line, "placeholder_text")
        width = CodeParser._extract_property_value(line, "width", 200)
        height = CodeParser._extract_property_value(line, "height", 30)
        x, y = CodeParser._extract_position(line)
        
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
    def _parse_checkbox(line: str) -> WidgetData:
        """Parse checkbox widget from code"""
        var_name = CodeParser._extract_variable_name(line)
        widget_id = var_name.replace("checkbox_", "")
        
        text = CodeParser._extract_property_value(line, "text")
        width = CodeParser._extract_property_value(line, "width", 200)
        height = CodeParser._extract_property_value(line, "height", 30)
        x, y = CodeParser._extract_position(line)
        
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
    def _parse_combobox(line: str) -> WidgetData:
        """Parse combobox widget from code"""
        var_name = CodeParser._extract_variable_name(line)
        widget_id = var_name.replace("combobox_", "")
        
        values = CodeParser._extract_property_value(line, "values")
        width = CodeParser._extract_property_value(line, "width", 200)
        height = CodeParser._extract_property_value(line, "height", 30)
        x, y = CodeParser._extract_position(line)
        
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
    def _parse_slider(line: str) -> WidgetData:
        """Parse slider widget from code"""
        var_name = CodeParser._extract_variable_name(line)
        widget_id = var_name.replace("slider_", "")
        
        from_val = CodeParser._extract_property_value(line, "from_", 0)
        to_val = CodeParser._extract_property_value(line, "to", 100)
        width = CodeParser._extract_property_value(line, "width", 200)
        height = CodeParser._extract_property_value(line, "height", 20)
        x, y = CodeParser._extract_position(line)
        
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
    def _parse_progressbar(line: str) -> WidgetData:
        """Parse progressbar widget from code"""
        var_name = CodeParser._extract_variable_name(line)
        widget_id = var_name.replace("progressbar_", "")
        
        width = CodeParser._extract_property_value(line, "width", 200)
        height = CodeParser._extract_property_value(line, "height", 20)
        x, y = CodeParser._extract_position(line)
        
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

class PreferencesWindow(ctk.CTkToplevel):
    """Comprehensive preferences window with multiple categories"""
    
    def __init__(self, parent_app, preferences_manager):
        super().__init__()
        self.parent_app = parent_app
        self.prefs_manager = preferences_manager
        self.original_prefs = asdict(preferences_manager.preferences)
        
        self.title("Preferences")
        self.geometry("800x600")
        self.minsize(600, 400)
        
        # Make this window modal
        self.transient(parent_app)
        self.grab_set()
        
        self.setup_ui()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def setup_ui(self):
        """Setup the preferences window UI"""
        # Main container with scrollable frame
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title = ctk.CTkLabel(main_frame, text="Preferences", font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(pady=(10, 20))
        
        # Create notebook for categories
        self.notebook = ctk.CTkTabview(main_frame)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create preference categories
        self.create_appearance_tab()
        self.create_window_tab()
        self.create_editor_tab()
        self.create_canvas_tab()
        self.create_widgets_tab()
        self.create_code_generation_tab()
        self.create_file_operations_tab()
        self.create_performance_tab()
        self.create_advanced_tab()
        
        # Bottom buttons
        self.create_bottom_buttons(main_frame)
    
    def create_appearance_tab(self):
        """Create appearance preferences tab"""
        tab = self.notebook.add("🎨 Appearance")
        
        # Appearance mode
        ctk.CTkLabel(tab, text="Appearance Mode:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 5))
        self.appearance_mode = ctk.CTkComboBox(tab, values=["light", "dark", "system"], width=200)
        self.appearance_mode.set(self.prefs_manager.get("appearance_mode"))
        self.appearance_mode.pack(anchor="w", pady=(0, 10))
        
        # Color theme
        ctk.CTkLabel(tab, text="Color Theme:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 5))
        self.color_theme = ctk.CTkComboBox(tab, values=["blue", "green", "dark-blue"], width=200)
        self.color_theme.set(self.prefs_manager.get("color_theme"))
        self.color_theme.pack(anchor="w", pady=(0, 10))
        
        # Custom colors section
        colors_frame = ctk.CTkFrame(tab)
        colors_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(colors_frame, text="Custom Colors:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=10)
        
        # Primary color
        primary_frame = ctk.CTkFrame(colors_frame)
        primary_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(primary_frame, text="Primary:").pack(side="left", padx=5)
        self.primary_color_btn = ctk.CTkButton(primary_frame, text="", width=50, height=25,
                                             fg_color=self.prefs_manager.get("custom_primary_color"),
                                             command=lambda: self.choose_color("custom_primary_color", self.primary_color_btn))
        self.primary_color_btn.pack(side="left", padx=5)
        
        # Secondary color
        secondary_frame = ctk.CTkFrame(colors_frame)
        secondary_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(secondary_frame, text="Secondary:").pack(side="left", padx=5)
        self.secondary_color_btn = ctk.CTkButton(secondary_frame, text="", width=50, height=25,
                                               fg_color=self.prefs_manager.get("custom_secondary_color"),
                                               command=lambda: self.choose_color("custom_secondary_color", self.secondary_color_btn))
        self.secondary_color_btn.pack(side="left", padx=5)
    
    def create_window_tab(self):
        """Create window preferences tab"""
        tab = self.notebook.add("🪟 Window")
        
        # Window size
        size_frame = ctk.CTkFrame(tab)
        size_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(size_frame, text="Window Size:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=10)
        
        size_input_frame = ctk.CTkFrame(size_frame)
        size_input_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(size_input_frame, text="Width:").pack(side="left", padx=5)
        self.window_width = ctk.CTkEntry(size_input_frame, width=80)
        self.window_width.insert(0, str(self.prefs_manager.get("window_width")))
        self.window_width.pack(side="left", padx=5)
        
        ctk.CTkLabel(size_input_frame, text="Height:").pack(side="left", padx=5)
        self.window_height = ctk.CTkEntry(size_input_frame, width=80)
        self.window_height.insert(0, str(self.prefs_manager.get("window_height")))
        self.window_height.pack(side="left", padx=5)
        
        # Window behavior
        behavior_frame = ctk.CTkFrame(tab)
        behavior_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(behavior_frame, text="Window Behavior:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=10)
        
        self.remember_position = ctk.CTkCheckBox(behavior_frame, text="Remember window position")
        self.remember_position.pack(anchor="w", padx=10, pady=5)
        if self.prefs_manager.get("remember_window_position"):
            self.remember_position.select()
        
        self.remember_size = ctk.CTkCheckBox(behavior_frame, text="Remember window size")
        self.remember_size.pack(anchor="w", padx=10, pady=5)
        if self.prefs_manager.get("remember_window_size"):
            self.remember_size.select()
        
        # Auto-save
        autosave_frame = ctk.CTkFrame(tab)
        autosave_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(autosave_frame, text="Auto-save Interval (seconds):", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=10)
        
        self.auto_save_interval = ctk.CTkEntry(autosave_frame, width=100)
        self.auto_save_interval.insert(0, str(self.prefs_manager.get("auto_save_interval")))
        self.auto_save_interval.pack(anchor="w", padx=10, pady=5)
    
    def create_editor_tab(self):
        """Create editor preferences tab"""
        tab = self.notebook.add("📝 Editor")
        
        # Font settings
        font_frame = ctk.CTkFrame(tab)
        font_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(font_frame, text="Font Settings:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=10)
        
        font_input_frame = ctk.CTkFrame(font_frame)
        font_input_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(font_input_frame, text="Family:").pack(side="left", padx=5)
        self.font_family = ctk.CTkEntry(font_input_frame, width=120)
        self.font_family.insert(0, self.prefs_manager.get("font_family"))
        self.font_family.pack(side="left", padx=5)
        
        ctk.CTkLabel(font_input_frame, text="Size:").pack(side="left", padx=5)
        self.font_size = ctk.CTkEntry(font_input_frame, width=60)
        self.font_size.insert(0, str(self.prefs_manager.get("font_size")))
        self.font_size.pack(side="left", padx=5)
        
        # Editor behavior
        behavior_frame = ctk.CTkFrame(tab)
        behavior_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(behavior_frame, text="Editor Behavior:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=10)
        
        self.show_line_numbers = ctk.CTkCheckBox(behavior_frame, text="Show line numbers")
        self.show_line_numbers.pack(anchor="w", padx=10, pady=2)
        if self.prefs_manager.get("show_line_numbers"):
            self.show_line_numbers.select()
        
        self.word_wrap = ctk.CTkCheckBox(behavior_frame, text="Word wrap")
        self.word_wrap.pack(anchor="w", padx=10, pady=2)
        if self.prefs_manager.get("word_wrap"):
            self.word_wrap.select()
        
        self.syntax_highlighting = ctk.CTkCheckBox(behavior_frame, text="Syntax highlighting")
        self.syntax_highlighting.pack(anchor="w", padx=10, pady=2)
        if self.prefs_manager.get("syntax_highlighting"):
            self.syntax_highlighting.select()
        
        self.auto_indent = ctk.CTkCheckBox(behavior_frame, text="Auto indent")
        self.auto_indent.pack(anchor="w", padx=10, pady=2)
        if self.prefs_manager.get("auto_indent"):
            self.auto_indent.select()
        
        # Tab settings
        tab_frame = ctk.CTkFrame(tab)
        tab_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(tab_frame, text="Tab Settings:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=10)
        
        tab_input_frame = ctk.CTkFrame(tab_frame)
        tab_input_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(tab_input_frame, text="Tab size:").pack(side="left", padx=5)
        self.tab_size = ctk.CTkEntry(tab_input_frame, width=60)
        self.tab_size.insert(0, str(self.prefs_manager.get("tab_size")))
        self.tab_size.pack(side="left", padx=5)
        
        self.use_spaces = ctk.CTkCheckBox(tab_input_frame, text="Use spaces for tabs")
        self.use_spaces.pack(side="left", padx=20)
        if self.prefs_manager.get("use_spaces_for_tabs"):
            self.use_spaces.select()
    
    def create_canvas_tab(self):
        """Create canvas preferences tab"""
        tab = self.notebook.add("🎨 Canvas")
        
        # Grid settings
        grid_frame = ctk.CTkFrame(tab)
        grid_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(grid_frame, text="Grid Settings:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=10)
        
        self.show_grid = ctk.CTkCheckBox(grid_frame, text="Show grid")
        self.show_grid.pack(anchor="w", padx=10, pady=2)
        if self.prefs_manager.get("show_grid"):
            self.show_grid.select()
        
        self.snap_to_grid = ctk.CTkCheckBox(grid_frame, text="Snap to grid")
        self.snap_to_grid.pack(anchor="w", padx=10, pady=2)
        if self.prefs_manager.get("snap_to_grid"):
            self.snap_to_grid.select()
        
        grid_size_frame = ctk.CTkFrame(grid_frame)
        grid_size_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(grid_size_frame, text="Grid size:").pack(side="left", padx=5)
        self.grid_size = ctk.CTkEntry(grid_size_frame, width=60)
        self.grid_size.insert(0, str(self.prefs_manager.get("grid_size")))
        self.grid_size.pack(side="left", padx=5)
        
        # Canvas colors
        colors_frame = ctk.CTkFrame(tab)
        colors_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(colors_frame, text="Canvas Colors:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=10)
        
        # Background color
        bg_frame = ctk.CTkFrame(colors_frame)
        bg_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(bg_frame, text="Background:").pack(side="left", padx=5)
        self.canvas_bg_btn = ctk.CTkButton(bg_frame, text="", width=50, height=25,
                                         fg_color=self.prefs_manager.get("canvas_background"),
                                         command=lambda: self.choose_color("canvas_background", self.canvas_bg_btn))
        self.canvas_bg_btn.pack(side="left", padx=5)
        
        # Grid color
        grid_color_frame = ctk.CTkFrame(colors_frame)
        grid_color_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(grid_color_frame, text="Grid:").pack(side="left", padx=5)
        self.grid_color_btn = ctk.CTkButton(grid_color_frame, text="", width=50, height=25,
                                          fg_color=self.prefs_manager.get("grid_color"),
                                          command=lambda: self.choose_color("grid_color", self.grid_color_btn))
        self.grid_color_btn.pack(side="left", padx=5)
    
    def create_widgets_tab(self):
        """Create widget defaults tab"""
        tab = self.notebook.add("🧩 Widgets")
        
        # Default widget sizes
        sizes_frame = ctk.CTkFrame(tab)
        sizes_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(sizes_frame, text="Default Widget Sizes:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=10)
        
        # Button defaults
        button_frame = ctk.CTkFrame(sizes_frame)
        button_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(button_frame, text="Button:").pack(side="left", padx=5)
        ctk.CTkLabel(button_frame, text="W:").pack(side="left", padx=5)
        self.button_width = ctk.CTkEntry(button_frame, width=60)
        self.button_width.insert(0, str(self.prefs_manager.get("default_button_width")))
        self.button_width.pack(side="left", padx=2)
        ctk.CTkLabel(button_frame, text="H:").pack(side="left", padx=5)
        self.button_height = ctk.CTkEntry(button_frame, width=60)
        self.button_height.insert(0, str(self.prefs_manager.get("default_button_height")))
        self.button_height.pack(side="left", padx=2)
        
        # Label defaults
        label_frame = ctk.CTkFrame(sizes_frame)
        label_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(label_frame, text="Label:").pack(side="left", padx=5)
        ctk.CTkLabel(label_frame, text="W:").pack(side="left", padx=5)
        self.label_width = ctk.CTkEntry(label_frame, width=60)
        self.label_width.insert(0, str(self.prefs_manager.get("default_label_width")))
        self.label_width.pack(side="left", padx=2)
        ctk.CTkLabel(label_frame, text="H:").pack(side="left", padx=5)
        self.label_height = ctk.CTkEntry(label_frame, width=60)
        self.label_height.insert(0, str(self.prefs_manager.get("default_label_height")))
        self.label_height.pack(side="left", padx=2)
    
    def create_code_generation_tab(self):
        """Create code generation preferences tab"""
        tab = self.notebook.add("⚙️ Code Generation")
        
        # Code style
        style_frame = ctk.CTkFrame(tab)
        style_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(style_frame, text="Code Style:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=10)
        
        self.code_style = ctk.CTkComboBox(style_frame, values=["pep8", "black", "custom"], width=200)
        self.code_style.set(self.prefs_manager.get("code_style"))
        self.code_style.pack(anchor="w", padx=10, pady=5)
        
        # Code generation options
        options_frame = ctk.CTkFrame(tab)
        options_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(options_frame, text="Generation Options:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=10)
        
        self.generate_comments = ctk.CTkCheckBox(options_frame, text="Generate comments")
        self.generate_comments.pack(anchor="w", padx=10, pady=2)
        if self.prefs_manager.get("generate_comments"):
            self.generate_comments.select()
        
        self.generate_docstrings = ctk.CTkCheckBox(options_frame, text="Generate docstrings")
        self.generate_docstrings.pack(anchor="w", padx=10, pady=2)
        if self.prefs_manager.get("generate_docstrings"):
            self.generate_docstrings.select()
        
        self.include_imports = ctk.CTkCheckBox(options_frame, text="Include imports")
        self.include_imports.pack(anchor="w", padx=10, pady=2)
        if self.prefs_manager.get("include_imports"):
            self.include_imports.select()
        
        self.auto_format_code = ctk.CTkCheckBox(options_frame, text="Auto-format code")
        self.auto_format_code.pack(anchor="w", padx=10, pady=2)
        if self.prefs_manager.get("auto_format_code"):
            self.auto_format_code.select()
    
    def create_file_operations_tab(self):
        """Create file operations preferences tab"""
        tab = self.notebook.add("📁 File Operations")
        
        # File behavior
        behavior_frame = ctk.CTkFrame(tab)
        behavior_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(behavior_frame, text="File Behavior:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=10)
        
        self.auto_save = ctk.CTkCheckBox(behavior_frame, text="Auto-save")
        self.auto_save.pack(anchor="w", padx=10, pady=2)
        if self.prefs_manager.get("auto_save"):
            self.auto_save.select()
        
        self.backup_files = ctk.CTkCheckBox(behavior_frame, text="Create backup files")
        self.backup_files.pack(anchor="w", padx=10, pady=2)
        if self.prefs_manager.get("backup_files"):
            self.backup_files.select()
        
        self.confirm_before_close = ctk.CTkCheckBox(behavior_frame, text="Confirm before closing")
        self.confirm_before_close.pack(anchor="w", padx=10, pady=2)
        if self.prefs_manager.get("confirm_before_close"):
            self.confirm_before_close.select()
        
        # Recent files
        recent_frame = ctk.CTkFrame(tab)
        recent_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(recent_frame, text="Recent Files:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=10)
        
        recent_input_frame = ctk.CTkFrame(recent_frame)
        recent_input_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(recent_input_frame, text="Max recent files:").pack(side="left", padx=5)
        self.max_recent_files = ctk.CTkEntry(recent_input_frame, width=60)
        self.max_recent_files.insert(0, str(self.prefs_manager.get("max_recent_files")))
        self.max_recent_files.pack(side="left", padx=5)
    
    def create_performance_tab(self):
        """Create performance preferences tab"""
        tab = self.notebook.add("⚡ Performance")
        
        # Animations
        anim_frame = ctk.CTkFrame(tab)
        anim_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(anim_frame, text="Animations:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=10)
        
        self.enable_animations = ctk.CTkCheckBox(anim_frame, text="Enable animations")
        self.enable_animations.pack(anchor="w", padx=10, pady=2)
        if self.prefs_manager.get("enable_animations"):
            self.enable_animations.select()
        
        anim_speed_frame = ctk.CTkFrame(anim_frame)
        anim_speed_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(anim_speed_frame, text="Animation speed (ms):").pack(side="left", padx=5)
        self.animation_speed = ctk.CTkEntry(anim_speed_frame, width=80)
        self.animation_speed.insert(0, str(self.prefs_manager.get("animation_speed")))
        self.animation_speed.pack(side="left", padx=5)
        
        # Performance options
        perf_frame = ctk.CTkFrame(tab)
        perf_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(perf_frame, text="Performance Options:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=10)
        
        self.enable_auto_complete = ctk.CTkCheckBox(perf_frame, text="Enable auto-complete")
        self.enable_auto_complete.pack(anchor="w", padx=10, pady=2)
        if self.prefs_manager.get("enable_auto_complete"):
            self.enable_auto_complete.select()
        
        self.enable_tooltips = ctk.CTkCheckBox(perf_frame, text="Enable tooltips")
        self.enable_tooltips.pack(anchor="w", padx=10, pady=2)
        if self.prefs_manager.get("enable_tooltips"):
            self.enable_tooltips.select()
        
        # Undo history
        undo_frame = ctk.CTkFrame(tab)
        undo_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(undo_frame, text="Undo History:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=10)
        
        undo_input_frame = ctk.CTkFrame(undo_frame)
        undo_input_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(undo_input_frame, text="Max undo steps:").pack(side="left", padx=5)
        self.max_undo_history = ctk.CTkEntry(undo_input_frame, width=80)
        self.max_undo_history.insert(0, str(self.prefs_manager.get("max_undo_history")))
        self.max_undo_history.pack(side="left", padx=5)
    
    def create_advanced_tab(self):
        """Create advanced preferences tab"""
        tab = self.notebook.add("🔧 Advanced")
        
        # Debug options
        debug_frame = ctk.CTkFrame(tab)
        debug_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(debug_frame, text="Debug Options:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=10)
        
        self.debug_mode = ctk.CTkCheckBox(debug_frame, text="Debug mode")
        self.debug_mode.pack(anchor="w", padx=10, pady=2)
        if self.prefs_manager.get("debug_mode"):
            self.debug_mode.select()
        
        # Log level
        log_frame = ctk.CTkFrame(tab)
        log_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(log_frame, text="Log Level:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=10)
        
        self.log_level = ctk.CTkComboBox(log_frame, values=["DEBUG", "INFO", "WARNING", "ERROR"], width=200)
        self.log_level.set(self.prefs_manager.get("log_level"))
        self.log_level.pack(anchor="w", padx=10, pady=5)
        
        # System options
        system_frame = ctk.CTkFrame(tab)
        system_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(system_frame, text="System Options:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=10)
        
        self.check_updates = ctk.CTkCheckBox(system_frame, text="Check for updates")
        self.check_updates.pack(anchor="w", padx=10, pady=2)
        if self.prefs_manager.get("check_updates"):
            self.check_updates.select()
        
        self.enable_telemetry = ctk.CTkCheckBox(system_frame, text="Enable telemetry")
        self.enable_telemetry.pack(anchor="w", padx=10, pady=2)
        if self.prefs_manager.get("enable_telemetry"):
            self.enable_telemetry.select()
        
        self.experimental_features = ctk.CTkCheckBox(system_frame, text="Enable experimental features")
        self.experimental_features.pack(anchor="w", padx=10, pady=2)
        if self.prefs_manager.get("experimental_features"):
            self.experimental_features.select()
    
    def create_bottom_buttons(self, parent):
        """Create bottom action buttons"""
        button_frame = ctk.CTkFrame(parent)
        button_frame.pack(fill="x", pady=(10, 0))
        
        # Reset to defaults button
        reset_btn = ctk.CTkButton(button_frame, text="Reset to Defaults", width=120, height=30,
                                 command=self.reset_to_defaults, font=ctk.CTkFont(size=12))
        reset_btn.pack(side="left", padx=10, pady=10)
        
        # Cancel button
        cancel_btn = ctk.CTkButton(button_frame, text="Cancel", width=80, height=30,
                                  command=self.on_cancel, font=ctk.CTkFont(size=12))
        cancel_btn.pack(side="right", padx=10, pady=10)
        
        # Apply button
        apply_btn = ctk.CTkButton(button_frame, text="Apply", width=80, height=30,
                                 command=self.on_apply, font=ctk.CTkFont(size=12))
        apply_btn.pack(side="right", padx=5, pady=10)
        
        # OK button
        ok_btn = ctk.CTkButton(button_frame, text="OK", width=80, height=30,
                              command=self.on_ok, font=ctk.CTkFont(size=12))
        ok_btn.pack(side="right", padx=5, pady=10)
    
    def choose_color(self, preference_key, button):
        """Open color chooser dialog"""
        color = colorchooser.askcolor(title=f"Choose {preference_key.replace('_', ' ').title()} Color")
        if color[1]:  # If a color was selected
            button.configure(fg_color=color[1])
            self.prefs_manager.set(preference_key, color[1])
    
    def reset_to_defaults(self):
        """Reset all preferences to default values"""
        if messagebox.askyesno("Reset Preferences", "Are you sure you want to reset all preferences to default values?"):
            self.prefs_manager.reset_to_defaults()
            self.destroy()
            # Reopen preferences window with defaults
            PreferencesWindow(self.parent_app, self.prefs_manager)
    
    def on_apply(self):
        """Apply current preferences without closing"""
        self.save_current_preferences()
        messagebox.showinfo("Preferences", "Preferences applied successfully!")
    
    def on_ok(self):
        """Apply preferences and close window"""
        self.save_current_preferences()
        self.destroy()
    
    def on_cancel(self):
        """Cancel changes and close window"""
        # Restore original preferences
        for key, value in self.original_prefs.items():
            self.prefs_manager.set(key, value)
        self.destroy()
    
    def on_close(self):
        """Handle window close event"""
        self.on_cancel()
    
    def save_current_preferences(self):
        """Save all current preference values"""
        # Appearance
        self.prefs_manager.set("appearance_mode", self.appearance_mode.get())
        self.prefs_manager.set("color_theme", self.color_theme.get())
        
        # Window
        try:
            self.prefs_manager.set("window_width", int(self.window_width.get()))
            self.prefs_manager.set("window_height", int(self.window_height.get()))
            self.prefs_manager.set("auto_save_interval", int(self.auto_save_interval.get()))
        except ValueError:
            pass
        
        self.prefs_manager.set("remember_window_position", self.remember_position.get() == 1)
        self.prefs_manager.set("remember_window_size", self.remember_size.get() == 1)
        
        # Editor
        self.prefs_manager.set("font_family", self.font_family.get())
        try:
            self.prefs_manager.set("font_size", int(self.font_size.get()))
            self.prefs_manager.set("tab_size", int(self.tab_size.get()))
        except ValueError:
            pass
        
        self.prefs_manager.set("use_spaces_for_tabs", self.use_spaces.get() == 1)
        self.prefs_manager.set("show_line_numbers", self.show_line_numbers.get() == 1)
        self.prefs_manager.set("word_wrap", self.word_wrap.get() == 1)
        self.prefs_manager.set("syntax_highlighting", self.syntax_highlighting.get() == 1)
        self.prefs_manager.set("auto_indent", self.auto_indent.get() == 1)
        
        # Canvas
        self.prefs_manager.set("show_grid", self.show_grid.get() == 1)
        self.prefs_manager.set("snap_to_grid", self.snap_to_grid.get() == 1)
        try:
            self.prefs_manager.set("grid_size", int(self.grid_size.get()))
        except ValueError:
            pass
        
        # Widgets
        try:
            self.prefs_manager.set("default_button_width", int(self.button_width.get()))
            self.prefs_manager.set("default_button_height", int(self.button_height.get()))
            self.prefs_manager.set("default_label_width", int(self.label_width.get()))
            self.prefs_manager.set("default_label_height", int(self.label_height.get()))
        except ValueError:
            pass
        
        # Code Generation
        self.prefs_manager.set("code_style", self.code_style.get())
        self.prefs_manager.set("generate_comments", self.generate_comments.get() == 1)
        self.prefs_manager.set("generate_docstrings", self.generate_docstrings.get() == 1)
        self.prefs_manager.set("include_imports", self.include_imports.get() == 1)
        self.prefs_manager.set("auto_format_code", self.auto_format_code.get() == 1)
        
        # File Operations
        self.prefs_manager.set("auto_save", self.auto_save.get() == 1)
        self.prefs_manager.set("backup_files", self.backup_files.get() == 1)
        self.prefs_manager.set("confirm_before_close", self.confirm_before_close.get() == 1)
        try:
            self.prefs_manager.set("max_recent_files", int(self.max_recent_files.get()))
        except ValueError:
            pass
        
        # Performance
        self.prefs_manager.set("enable_animations", self.enable_animations.get() == 1)
        self.prefs_manager.set("enable_auto_complete", self.enable_auto_complete.get() == 1)
        self.prefs_manager.set("enable_tooltips", self.enable_tooltips.get() == 1)
        try:
            self.prefs_manager.set("animation_speed", int(self.animation_speed.get()))
            self.prefs_manager.set("max_undo_history", int(self.max_undo_history.get()))
        except ValueError:
            pass
        
        # Advanced
        self.prefs_manager.set("debug_mode", self.debug_mode.get() == 1)
        self.prefs_manager.set("log_level", self.log_level.get())
        self.prefs_manager.set("check_updates", self.check_updates.get() == 1)
        self.prefs_manager.set("enable_telemetry", self.enable_telemetry.get() == 1)
        self.prefs_manager.set("experimental_features", self.experimental_features.get() == 1)

class GUIBuilderApp(ctk.CTk):
    """Main application class - Professional Python GUI Builder MVP"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize preferences manager
        self.prefs_manager = PreferencesManager()
        
        # Apply appearance preferences
        self.apply_appearance_preferences()
        
        self.title("Professional Python GUI Builder - MVP")
        
        # Apply window preferences
        self.apply_window_preferences()
        
        self.minsize(1000, 700)
        
        # Application state
        self.current_file = None
        self.recent_files = []
        self.project_modified = False
        
        # Code editor pop-out state
        self.code_editor_popped_out = False
        self.pop_out_window = None
        
        # Window properties
        self.window_properties = {
            'title': 'Generated GUI',
            'width': 800,
            'height': 600,
            'resizable': True,
            'min_width': 400,
            'min_height': 300,
            'center_on_screen': True
        }
        
        # Configure grid weights for resizable panels
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.setup_ui()
        self.setup_menu()
        self.setup_toolbar()
        self.setup_global_bindings()
        self.load_recent_files()
        
        # Handle window close events
        self.protocol("WM_DELETE_WINDOW", self.on_main_window_close)
    
    def setup_ui(self):
        """Setup the main UI with Visual Studio-like layout"""
        # Enhanced Status Bar (create first)
        self.setup_status_bar()
        
        # Main content frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Widget Toolbox (Left Panel)
        self.toolbox = WidgetToolbox(self.main_frame, self.on_widget_drag_start)
        self.toolbox.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=0)
        
        # Design Canvas (Center Panel)
        canvas_frame = ctk.CTkFrame(self.main_frame)
        canvas_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=0)
        canvas_frame.grid_columnconfigure(0, weight=1)
        canvas_frame.grid_rowconfigure(0, weight=1)
        
        self.canvas = DesignCanvas(canvas_frame, self.on_widget_select, self.status_bar)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        
        # Properties Editor (Right Panel)
        self.properties_editor = PropertiesEditor(self.main_frame, self.on_property_change)
        self.properties_editor.grid(row=0, column=2, sticky="nsew", padx=(5, 0), pady=0)
        
        # Code Editor Panel (Initially hidden)
        self.setup_code_editor()
    
    def setup_code_editor(self):
        """Setup the code editor panel"""
        # Code editor frame (initially hidden)
        self.code_editor_frame = ctk.CTkFrame(self.main_frame)
        self.code_editor_frame.grid(row=0, column=3, sticky="nsew", padx=(5, 0), pady=0)
        self.code_editor_frame.grid_remove()  # Hide initially
        
        # Code editor
        self.code_editor = CodeEditor(self.code_editor_frame, self.on_code_change)
        self.code_editor.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Code editor controls
        self.code_controls_frame = ctk.CTkFrame(self.code_editor_frame)
        self.code_controls_frame.pack(fill="x", padx=5, pady=(0, 5))
        
        # Control buttons
        self.code_sync_button = ctk.CTkButton(
            self.code_controls_frame, text="🔄 Sync from Design", width=120, height=25,
            command=self.sync_code_from_design, font=ctk.CTkFont(size=10)
        )
        self.code_sync_button.pack(side="left", padx=5, pady=5)
        
        self.code_validate_button = ctk.CTkButton(
            self.code_controls_frame, text="✅ Validate", width=80, height=25,
            command=self.validate_code, font=ctk.CTkFont(size=10)
        )
        self.code_validate_button.pack(side="left", padx=5, pady=5)
        
        self.code_run_button = ctk.CTkButton(
            self.code_controls_frame, text="▶️ Run Code", width=80, height=25,
            command=self.run_generated_code, font=ctk.CTkFont(size=10)
        )
        self.code_run_button.pack(side="left", padx=5, pady=5)
        
        self.code_export_button = ctk.CTkButton(
            self.code_controls_frame, text="💾 Export", width=80, height=25,
            command=self.export_edited_code, font=ctk.CTkFont(size=10)
        )
        self.code_export_button.pack(side="right", padx=5, pady=5)
        
        # Pop-out button
        self.code_popout_button = ctk.CTkButton(
            self.code_controls_frame, text="📤 Pop Out", width=80, height=25,
            command=self.pop_code_editor_out, font=ctk.CTkFont(size=10)
        )
        self.code_popout_button.pack(side="right", padx=5, pady=5)
    
    def setup_toolbar(self):
        """Setup the professional toolbar"""
        self.toolbar_frame = ctk.CTkFrame(self, height=40)
        self.toolbar_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=5, pady=(5, 0))
        self.toolbar_frame.grid_propagate(False)
        
        # File operations
        self.toolbar_new = ctk.CTkButton(
            self.toolbar_frame, text="📄 New", width=80, height=30,
            command=self.new_project, font=ctk.CTkFont(size=12)
        )
        self.toolbar_new.pack(side="left", padx=(5, 2), pady=5)
        
        self.toolbar_open = ctk.CTkButton(
            self.toolbar_frame, text="📂 Open", width=80, height=30,
            command=self.open_project, font=ctk.CTkFont(size=12)
        )
        self.toolbar_open.pack(side="left", padx=2, pady=5)
        
        self.toolbar_save = ctk.CTkButton(
            self.toolbar_frame, text="💾 Save", width=80, height=30,
            command=self.save_project, font=ctk.CTkFont(size=12)
        )
        self.toolbar_save.pack(side="left", padx=2, pady=5)
        
        # Separator
        separator1 = ctk.CTkFrame(self.toolbar_frame, width=2, height=30)
        separator1.pack(side="left", padx=10, pady=5)
        
        # Design operations
        self.toolbar_preview = ctk.CTkButton(
            self.toolbar_frame, text="👁️ Preview", width=90, height=30,
            command=self.preview_gui, font=ctk.CTkFont(size=12)
        )
        self.toolbar_preview.pack(side="left", padx=2, pady=5)
        
        self.toolbar_export = ctk.CTkButton(
            self.toolbar_frame, text="📤 Export", width=90, height=30,
            command=self.export_python, font=ctk.CTkFont(size=12)
        )
        self.toolbar_export.pack(side="left", padx=2, pady=5)
        
        # Separator
        separator2 = ctk.CTkFrame(self.toolbar_frame, width=2, height=30)
        separator2.pack(side="left", padx=10, pady=5)
        
        # View operations
        self.toolbar_grid = ctk.CTkButton(
            self.toolbar_frame, text="⊞ Grid", width=70, height=30,
            command=self.toggle_grid, font=ctk.CTkFont(size=12)
        )
        self.toolbar_grid.pack(side="left", padx=2, pady=5)
        
        self.toolbar_clear = ctk.CTkButton(
            self.toolbar_frame, text="🗑️ Clear", width=70, height=30,
            command=self.clear_canvas, font=ctk.CTkFont(size=12)
        )
        self.toolbar_clear.pack(side="left", padx=2, pady=5)
        
        # Separator
        separator3 = ctk.CTkFrame(self.toolbar_frame, width=2, height=30)
        separator3.pack(side="left", padx=10, pady=5)
        
        # Code editor toggle
        self.toolbar_code = ctk.CTkButton(
            self.toolbar_frame, text="📝 Code", width=70, height=30,
            command=self.toggle_code_view, font=ctk.CTkFont(size=12)
        )
        self.toolbar_code.pack(side="left", padx=2, pady=5)
        
        # Right side - mode toggle button
        self.mode_toggle_button = ctk.CTkButton(
            self.toolbar_frame, text="🎨 Design Mode", width=120, height=30,
            command=self.toggle_code_view, font=ctk.CTkFont(size=11)
        )
        self.mode_toggle_button.pack(side="right", padx=10, pady=5)
    
    def setup_status_bar(self):
        """Setup enhanced status bar with multiple sections"""
        self.status_frame = ctk.CTkFrame(self, height=25)
        self.status_frame.grid(row=2, column=0, columnspan=3, sticky="ew", padx=5, pady=(0, 5))
        self.status_frame.grid_propagate(False)
        
        # Left section - main status
        self.status_bar = ctk.CTkLabel(
            self.status_frame, text="Ready", anchor="w",
            font=ctk.CTkFont(size=10)
        )
        self.status_bar.pack(side="left", padx=5, pady=2)
        
        # Middle section - widget count
        self.widget_count_label = ctk.CTkLabel(
            self.status_frame, text="Widgets: 0", anchor="w",
            font=ctk.CTkFont(size=10)
        )
        self.widget_count_label.pack(side="left", padx=20, pady=2)
        
        # Right section - project info
        self.project_info_label = ctk.CTkLabel(
            self.status_frame, text="No project", anchor="e",
            font=ctk.CTkFont(size=10)
        )
        self.project_info_label.pack(side="right", padx=5, pady=2)
    
    def setup_menu(self):
        """Setup the menu bar"""
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_project, accelerator="Ctrl+N")
        file_menu.add_command(label="Open", command=self.open_project, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Save", command=self.save_project, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As", command=self.save_project_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        
        # Recent files submenu
        self.recent_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Recent Files", menu=self.recent_menu)
        self.update_recent_menu()
        
        file_menu.add_separator()
        file_menu.add_command(label="Export Python", command=self.export_python, accelerator="Ctrl+E")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit, accelerator="Alt+F4")
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Toggle Grid", command=self.toggle_grid, accelerator="Ctrl+G")
        view_menu.add_command(label="Toggle Grid Snap", command=self.toggle_grid_snap, accelerator="Ctrl+Shift+G")
        view_menu.add_command(label="Toggle Window Boundary", command=self.toggle_window_boundary, accelerator="Ctrl+B")
        view_menu.add_command(label="Toggle Code View", command=self.toggle_code_view, accelerator="Ctrl+Shift+V")
        view_menu.add_separator()
        
        # Theme submenu
        theme_menu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label="Theme", menu=theme_menu)
        theme_menu.add_command(label="Light Theme", command=lambda: self.set_theme("light"))
        theme_menu.add_command(label="Dark Theme", command=lambda: self.set_theme("dark"))
        theme_menu.add_command(label="System Theme", command=lambda: self.set_theme("system"))
        theme_menu.add_separator()
        theme_menu.add_command(label="Blue Theme", command=lambda: self.set_color_theme("blue"))
        theme_menu.add_command(label="Green Theme", command=lambda: self.set_color_theme("green"))
        theme_menu.add_command(label="Dark Blue Theme", command=lambda: self.set_color_theme("dark-blue"))
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=lambda: self.canvas.on_undo(None), accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=lambda: self.canvas.on_redo(None), accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=lambda: self.canvas.on_cut(None), accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=lambda: self.canvas.on_copy(None), accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=lambda: self.canvas.on_paste(None), accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Duplicate", command=lambda: self.canvas.on_duplicate(None), accelerator="Ctrl+D")
        edit_menu.add_command(label="Select All", command=lambda: self.canvas.on_select_all(None), accelerator="Ctrl+A")
        edit_menu.add_command(label="Delete", command=lambda: self.canvas.on_delete_key(None), accelerator="Del")
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Preview", command=self.preview_gui, accelerator="F5")
        tools_menu.add_command(label="Clear Canvas", command=self.clear_canvas)
        tools_menu.add_separator()
        tools_menu.add_command(label="Preferences", command=self.show_preferences, accelerator="Ctrl+,")
        tools_menu.add_command(label="Window Properties", command=self.show_window_properties)
        tools_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts)
        tools_menu.add_command(label="About", command=self.show_about)
    
    def setup_global_bindings(self):
        """Setup global keyboard bindings"""
        # Bind delete key globally
        self.bind_all("<KeyPress-Delete>", self.on_global_delete)
        self.bind_all("<KeyPress-BackSpace>", self.on_global_delete)
        # Bind other common shortcuts globally
        self.bind_all("<Control-c>", self.on_global_copy)
        self.bind_all("<Control-v>", self.on_global_paste)
        self.bind_all("<Control-x>", self.on_global_cut)
        self.bind_all("<Control-z>", self.on_global_undo)
        self.bind_all("<Control-y>", self.on_global_redo)
        self.bind_all("<Control-s>", self.on_global_save)
        self.bind_all("<Control-n>", self.on_global_new)
        self.bind_all("<Control-o>", self.on_global_open)
        self.bind_all("<F5>", self.on_global_preview)
        self.bind_all("<Escape>", self.on_global_escape)
        self.bind_all("<Control-g>", self.on_global_toggle_grid)
        self.bind_all("<Control-Shift-G>", self.on_global_toggle_grid_snap)
        self.bind_all("<Control-e>", self.on_global_export)
        self.bind_all("<Control-Shift-V>", self.on_global_toggle_code_view)
        self.bind_all("<Control-b>", self.on_global_toggle_window_boundary)
        self.bind_all("<Control-comma>", self.on_global_preferences)
    
    def on_global_delete(self, event):
        """Global delete key handler"""
        # Check if focus is on a text input widget in properties editor
        if hasattr(self, 'properties_editor'):
            focused_widget = self.focus_get()
            if focused_widget and self.is_properties_text_widget(focused_widget):
                # Don't delete widget if typing in properties editor
                return "break"
            
            # Additional check: if any property widget has focus, don't delete
            if hasattr(self.properties_editor, 'property_widgets'):
                for prop_widget in self.properties_editor.property_widgets.values():
                    if prop_widget == focused_widget or self.is_widget_or_child_focused(prop_widget):
                        return "break"
        
        if hasattr(self, 'canvas') and self.canvas.selected_widget_id:
            self.canvas.on_delete_key(event)
        return "break"
    
    def is_properties_text_widget(self, widget):
        """Check if the widget is a text input in the properties editor"""
        if not hasattr(self, 'properties_editor'):
            return False
        
        # Check if the widget is within the properties editor
        try:
            # Walk up the widget hierarchy to see if we're in the properties editor
            current = widget
            while current:
                if current == self.properties_editor:
                    # Check if it's a text input widget (CTkEntry)
                    if hasattr(widget, '_entry') or str(type(widget)).find('CTkEntry') != -1:
                        return True
                    # Also check for CTkTextbox
                    if str(type(widget)).find('CTkTextbox') != -1:
                        return True
                    break
                current = current.master
        except:
            pass
        
        # Additional check: if any property widget has focus, don't delete
        if hasattr(self.properties_editor, 'property_widgets'):
            for prop_widget in self.properties_editor.property_widgets.values():
                if prop_widget == widget or self.is_widget_or_child_focused(prop_widget):
                    return True
        
        return False
    
    def is_widget_or_child_focused(self, widget):
        """Check if the widget or any of its children has focus"""
        try:
            focused_widget = self.focus_get()
            if not focused_widget:
                return False
            
            # Check if the focused widget is the same as our widget
            if focused_widget == widget:
                return True
            
            # Check if the focused widget is a child of our widget
            current = focused_widget
            while current:
                if current == widget:
                    return True
                current = current.master
        except:
            pass
        
        return False
    
    def on_global_copy(self, event):
        """Global copy key handler"""
        if hasattr(self, 'canvas'):
            self.canvas.on_copy(event)
        return "break"
    
    def on_global_paste(self, event):
        """Global paste key handler"""
        if hasattr(self, 'canvas'):
            self.canvas.on_paste(event)
        return "break"
    
    def on_global_cut(self, event):
        """Global cut key handler"""
        if hasattr(self, 'canvas'):
            self.canvas.on_cut(event)
        return "break"
    
    def on_global_undo(self, event):
        """Global undo key handler"""
        if hasattr(self, 'canvas'):
            self.canvas.on_undo(event)
        return "break"
    
    def on_global_redo(self, event):
        """Global redo key handler"""
        if hasattr(self, 'canvas'):
            self.canvas.on_redo(event)
        return "break"
    
    def on_global_save(self, event):
        """Global save key handler"""
        self.save_project()
        return "break"
    
    def on_global_new(self, event):
        """Global new key handler"""
        self.new_project()
        return "break"
    
    def on_global_open(self, event):
        """Global open key handler"""
        self.open_project()
        return "break"
    
    def on_global_preview(self, event):
        """Global preview key handler"""
        self.preview_gui()
        return "break"
    
    def on_global_escape(self, event):
        """Global escape key handler"""
        if hasattr(self, 'canvas'):
            self.canvas.on_escape(event)
        return "break"
    
    def on_global_toggle_grid(self, event):
        """Global toggle grid key handler"""
        self.toggle_grid()
        return "break"
    
    def on_global_toggle_grid_snap(self, event):
        """Global toggle grid snap key handler"""
        self.toggle_grid_snap()
        return "break"
    
    def on_global_export(self, event):
        """Global export key handler"""
        self.export_python()
        return "break"
    
    def on_global_toggle_code_view(self, event):
        """Global toggle code view key handler"""
        print("Code view toggle shortcut triggered!")  # Debug message
        self.toggle_code_view()
        return "break"
    
    def on_global_toggle_window_boundary(self, event):
        """Global toggle window boundary handler"""
        self.toggle_window_boundary()
        return "break"
    
    def on_global_preferences(self, event):
        """Global preferences key handler"""
        self.show_preferences()
        return "break"
    
    def on_widget_drag_start(self, widget_type: WidgetType):
        """Handle widget drag start from toolbox"""
        self.status_bar.configure(text=f"Drag {widget_type.value} to canvas")
    
    def on_widget_select(self, widget_data: Optional[WidgetData]):
        """Handle widget selection"""
        self.properties_editor.set_widget(widget_data)
        if widget_data:
            self.status_bar.configure(text=f"Selected: {widget_data.type.value}")
        else:
            self.status_bar.configure(text="No widget selected")
    
    def on_property_change(self, property_name: str, value: Any):
        """Handle property change"""
        if self.canvas.selected_widget_id:
            self.canvas.update_widget_property(self.canvas.selected_widget_id, property_name, value)
    
    def new_project(self):
        """Create a new project"""
        if self.project_modified:
            if not messagebox.askyesno("Save Changes", "Current project has unsaved changes. Save before creating new project?"):
                return
            self.save_project()
        
        self.canvas.widgets.clear()
        self.canvas.delete("all")
        self.canvas.draw_grid()
        self.canvas.deselect_all()
        self.current_file = None
        self.project_modified = False
        self.update_status_info()
        self.status_bar.configure(text="New project created")
        self.mode_toggle_button.configure(text="🎨 Design Mode")
    
    def open_project(self):
        """Open a project file"""
        if self.project_modified:
            if not messagebox.askyesno("Save Changes", "Current project has unsaved changes. Save before opening new project?"):
                return
            self.save_project()
        
        file_path = filedialog.askopenfilename(
            title="Open Project",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            self.load_project_from_path(file_path)
    
    def save_project(self):
        """Save the current project"""
        if not hasattr(self, 'current_file') or not self.current_file:
            self.save_project_as()
        else:
            self.save_to_file(self.current_file)
    
    def save_project_as(self):
        """Save project as new file"""
        file_path = filedialog.asksaveasfilename(
            title="Save Project As",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            self.current_file = file_path
            self.save_to_file(file_path)
    
    def save_to_file(self, file_path: str):
        """Save project to file"""
        try:
            data = {
                'widgets': [widget.to_dict() for widget in self.canvas.widgets.values()],
                'window_properties': self.window_properties
            }
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            self.current_file = file_path
            self.add_to_recent_files(file_path)
            self.project_modified = False
            self.update_status_info()
            self.status_bar.configure(text=f"Project saved: {os.path.basename(file_path)}")
            self.mode_toggle_button.configure(text=f"💾 Saved: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save project: {str(e)}")
    
    def export_python(self):
        """Export as Python file with automatic validation"""
        if not self.canvas.widgets:
            messagebox.showwarning("No Widgets", "No widgets to export. Add some widgets to your design first.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export Python Code",
            defaultextension=".py",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )
        if file_path:
            try:
                # Generate code with automatic ID cleaning and window properties
                code = CodeGenerator.generate_code(self.canvas.widgets, self.window_properties)
                
                # Validate the generated code for syntax errors
                is_valid, validation_message = CodeGenerator.validate_generated_code(code)
                if not is_valid:
                    error_msg = f"Generated code validation failed: {validation_message}"
                    self.status_bar.configure(text="Code validation failed")
                    messagebox.showerror("Code Validation Error", error_msg)
                    return
                
                # Write the validated code
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(code)
                
                self.status_bar.configure(text=f"Python code exported: {os.path.basename(file_path)}")
                self.mode_toggle_button.configure(text=f"📤 Exported: {os.path.basename(file_path)}")
                messagebox.showinfo("Export Successful", 
                    f"Python code successfully exported and validated:\n{file_path}\n\n"
                    f"✅ All widget IDs cleaned for valid Python syntax\n"
                    f"✅ Code syntax validated\n"
                    f"✅ Ready to run!")
            except Exception as e:
                error_msg = f"Failed to export Python code: {str(e)}"
                self.status_bar.configure(text="Export failed")
                messagebox.showerror("Export Error", error_msg)
    
    def toggle_grid(self):
        """Toggle grid display"""
        self.canvas.show_grid = not self.canvas.show_grid
        self.canvas.draw_grid()
        self.status_bar.configure(text=f"Grid {'enabled' if self.canvas.show_grid else 'disabled'}")
    
    def toggle_grid_snap(self):
        """Toggle grid snapping"""
        self.canvas.snap_to_grid = not self.canvas.snap_to_grid
        self.status_bar.configure(text=f"Grid snap {'enabled' if self.canvas.snap_to_grid else 'disabled'}")
    
    def toggle_window_boundary(self):
        """Toggle window boundary visibility"""
        self.canvas.window_boundary_visible = not self.canvas.window_boundary_visible
        status = "shown" if self.canvas.window_boundary_visible else "hidden"
        self.status_bar.configure(text=f"Window boundary {status}")
        
        # Redraw the boundary if showing
        if self.canvas.window_boundary_visible:
            self.canvas.draw_window_boundary()
        else:
            self.canvas.delete("window_boundary")
            self.canvas.delete("boundary_warning")
    
    def toggle_code_view(self):
        """Toggle code view panel or pop-out window"""
        print("Toggle code view called!")  # Debug message
        try:
            if self.code_editor_popped_out:
                # Code editor is popped out - bring it back in
                self.pop_code_editor_back_in()
            elif self.code_editor_frame.winfo_viewable():
                # Hide code editor - switch to Design Mode
                self.code_editor_frame.grid_remove()
                self.status_bar.configure(text="Switched to Design Mode")
                self.mode_toggle_button.configure(text="🎨 Design Mode")
                print("Code editor hidden - Design Mode")
            else:
                # Show code editor - switch to Code Mode
                self.code_editor_frame.grid()
                self.sync_code_from_design()  # Load current design code
                self.status_bar.configure(text="Switched to Code Mode")
                self.mode_toggle_button.configure(text="📝 Code Mode")
                print("Code editor shown - Code Mode")
        except Exception as e:
            print(f"Error in toggle_code_view: {e}")
            self.status_bar.configure(text=f"Error: {str(e)}")
    
    def pop_code_editor_out(self):
        """Pop the code editor out into a separate window"""
        try:
            # Get current code content
            current_code = self.code_editor.get_code() if hasattr(self, 'code_editor') else ""
            
            # Create pop-out window
            self.pop_out_window = PopOutCodeEditor(
                self, 
                self.on_code_change, 
                self.handle_popout_window_close
            )
            
            # Set the code content in the pop-out window
            if current_code:
                self.pop_out_window.set_code(current_code)
            else:
                # Sync from design if no current code
                self.sync_code_from_design()
                if hasattr(self, 'code_editor'):
                    current_code = self.code_editor.get_code()
                    self.pop_out_window.set_code(current_code)
            
            # Hide the embedded code editor
            self.code_editor_frame.grid_remove()
            
            # Update state
            self.code_editor_popped_out = True
            self.status_bar.configure(text="Code Editor popped out")
            self.mode_toggle_button.configure(text="📌 Pop Back In")
            
        except Exception as e:
            print(f"Error popping out code editor: {e}")
            self.status_bar.configure(text=f"Error: {str(e)}")
    
    def pop_code_editor_back_in(self):
        """Pop the code editor back into the main window"""
        try:
            # Get code from pop-out window if it exists
            if self.pop_out_window and hasattr(self.pop_out_window, 'get_code'):
                current_code = self.pop_out_window.get_code()
                # Update the embedded code editor with the current code
                if hasattr(self, 'code_editor'):
                    self.code_editor.set_code(current_code)
            
            # Close the pop-out window
            if self.pop_out_window:
                self.pop_out_window.destroy()
                self.pop_out_window = None
            
            # Show the embedded code editor
            self.code_editor_frame.grid()
            
            # Update state
            self.code_editor_popped_out = False
            self.status_bar.configure(text="Code Editor popped back in")
            self.mode_toggle_button.configure(text="📝 Code Mode")
            
        except Exception as e:
            print(f"Error popping code editor back in: {e}")
            self.status_bar.configure(text=f"Error: {str(e)}")
    
    def handle_popout_window_close(self):
        """Handle when the pop-out window is closed externally"""
        try:
            # Reset state without trying to get code from destroyed window
            self.code_editor_popped_out = False
            self.pop_out_window = None
            
            # Show the embedded code editor
            self.code_editor_frame.grid()
            
            # Update UI
            self.status_bar.configure(text="Code Editor window closed - back to embedded view")
            self.mode_toggle_button.configure(text="📝 Code Mode")
            
        except Exception as e:
            print(f"Error handling pop-out window close: {e}")
            self.status_bar.configure(text=f"Error: {str(e)}")
    
    def on_main_window_close(self):
        """Handle main window close event"""
        try:
            # Save window preferences before closing
            self.save_window_preferences()
            
            # Close pop-out window if it exists
            if self.pop_out_window:
                self.pop_out_window.destroy()
                self.pop_out_window = None
            
            # Close the main application
            self.destroy()
            
        except Exception as e:
            print(f"Error closing main window: {e}")
            # Force close even if there's an error
            self.destroy()
    
    def preview_gui(self):
        """Preview the generated GUI"""
        if not self.canvas.widgets:
            messagebox.showwarning("No Widgets", "No widgets to preview. Add some widgets to your design first.")
            return
        
        try:
            # Calculate preview window size based on window properties
            window_props = self.window_properties
            if window_props.get('auto_fit', True) and self.canvas.widgets:
                max_x = max(widget.x + widget.width for widget in self.canvas.widgets.values()) + 50
                max_y = max(widget.y + widget.height for widget in self.canvas.widgets.values()) + 50
                preview_width = max(window_props['width'], max_x) + 100  # Extra space for controls
                preview_height = max(window_props['height'], max_y) + 150  # Extra space for controls
            else:
                preview_width = window_props['width'] + 100
                preview_height = window_props['height'] + 150
            
            # Limit preview size to screen size
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            preview_width = min(preview_width, screen_width - 100)
            preview_height = min(preview_height, screen_height - 100)
            
            # Create preview window
            preview_window = ctk.CTkToplevel(self)
            preview_window.title(f"GUI Preview - {window_props['title']}")
            preview_window.geometry(f"{preview_width}x{preview_height}")
            preview_window.transient(self)
            
            # Center the preview window
            preview_window.update_idletasks()
            x = (screen_width // 2) - (preview_width // 2)
            y = (screen_height // 2) - (preview_height // 2)
            preview_window.geometry(f"{preview_width}x{preview_height}+{x}+{y}")
            
            # Add header with controls
            header_frame = ctk.CTkFrame(preview_window)
            header_frame.pack(fill="x", padx=10, pady=5)
            
            # Title and size info
            title_label = ctk.CTkLabel(
                header_frame,
                text=f"Preview: {window_props['title']} ({window_props['width']}×{window_props['height']})",
                font=ctk.CTkFont(size=16, weight="bold")
            )
            title_label.pack(side="left", padx=10, pady=5)
            
            # Close button
            close_button = ctk.CTkButton(
                header_frame,
                text="Close Preview",
                command=preview_window.destroy,
                width=120,
                height=30
            )
            close_button.pack(side="right", padx=10, pady=5)
            
            # Create a canvas for the preview to show exact positioning
            preview_canvas = ctk.CTkCanvas(
                preview_window,
                width=window_props['width'],
                height=window_props['height'],
                bg="#2b2b2b",
                highlightthickness=2,
                highlightbackground="#ff6b6b"
            )
            preview_canvas.pack(pady=10)
            
            # Create preview widgets with exact positioning
            for widget_data in self.canvas.widgets.values():
                self.create_preview_widget_canvas(preview_canvas, widget_data)
            
            # Add info label
            info_label = ctk.CTkLabel(
                preview_window,
                text=f"Window size: {window_props['width']}×{window_props['height']} | Widgets: {len(self.canvas.widgets)}",
                font=ctk.CTkFont(size=12)
            )
            info_label.pack(pady=5)
            
            self.status_bar.configure(text="Preview window opened")
            self.mode_toggle_button.configure(text="👁️ Preview Active")
            
        except Exception as e:
            error_msg = f"Failed to create preview: {str(e)}"
            self.status_bar.configure(text="Preview failed")
            messagebox.showerror("Preview Error", error_msg)
    
    def create_preview_widget(self, parent, widget_data: WidgetData):
        """Create a preview widget in the preview window"""
        try:
            # Get widget properties
            text = widget_data.properties.get('text', {}).get('value', '')
            width = widget_data.properties.get('width', {}).get('value', 100)
            height = widget_data.properties.get('height', {}).get('value', 30)
            
            # Create the appropriate widget type
            if widget_data.type == WidgetType.BUTTON:
                widget = ctk.CTkButton(
                    parent,
                    text=text,
                    width=width,
                    height=height
                )
            elif widget_data.type == WidgetType.LABEL:
                widget = ctk.CTkLabel(
                    parent,
                    text=text,
                    width=width,
                    height=height
                )
            elif widget_data.type == WidgetType.ENTRY:
                widget = ctk.CTkEntry(
                    parent,
                    width=width,
                    height=height,
                    placeholder_text=text
                )
            elif widget_data.type == WidgetType.CHECKBOX:
                widget = ctk.CTkCheckBox(
                    parent,
                    text=text,
                    width=width,
                    height=height
                )
            elif widget_data.type == WidgetType.COMBOBOX:
                options = widget_data.properties.get('options', {}).get('value', [])
                widget = ctk.CTkComboBox(
                    parent,
                    width=width,
                    height=height,
                    values=options if options else ["Option 1", "Option 2"]
                )
            elif widget_data.type == WidgetType.SLIDER:
                widget = ctk.CTkSlider(
                    parent,
                    width=width,
                    height=height
                )
            elif widget_data.type == WidgetType.PROGRESSBAR:
                widget = ctk.CTkProgressBar(
                    parent,
                    width=width,
                    height=height
                )
            else:
                # Fallback for unknown types
                widget = ctk.CTkLabel(
                    parent,
                    text=f"Unknown widget: {widget_data.type.value}",
                    width=width,
                    height=height
                )
            
            # Pack the widget
            widget.pack(pady=5, padx=10, fill="x")
            
        except Exception as e:
            # Create error widget if preview fails
            error_widget = ctk.CTkLabel(
                parent,
                text=f"Error creating {widget_data.type.value}: {str(e)}",
                text_color="red"
            )
            error_widget.pack(pady=5, padx=10, fill="x")
    
    def create_preview_widget_canvas(self, canvas, widget_data: WidgetData):
        """Create a preview widget on a canvas with exact positioning"""
        try:
            # Get widget properties
            text = widget_data.properties.get('text', {}).get('value', '')
            width = widget_data.properties.get('width', {}).get('value', 100)
            height = widget_data.properties.get('height', {}).get('value', 30)
            
            # Create a frame to hold the widget
            widget_frame = ctk.CTkFrame(canvas)
            
            # Create the appropriate widget type
            if widget_data.type == WidgetType.BUTTON:
                widget = ctk.CTkButton(
                    widget_frame,
                    text=text,
                    width=width,
                    height=height
                )
            elif widget_data.type == WidgetType.LABEL:
                widget = ctk.CTkLabel(
                    widget_frame,
                    text=text,
                    width=width,
                    height=height
                )
            elif widget_data.type == WidgetType.ENTRY:
                widget = ctk.CTkEntry(
                    widget_frame,
                    width=width,
                    height=height,
                    placeholder_text=text
                )
            elif widget_data.type == WidgetType.CHECKBOX:
                widget = ctk.CTkCheckBox(
                    widget_frame,
                    text=text,
                    width=width,
                    height=height
                )
            elif widget_data.type == WidgetType.COMBOBOX:
                options = widget_data.properties.get('options', {}).get('value', [])
                widget = ctk.CTkComboBox(
                    widget_frame,
                    width=width,
                    height=height,
                    values=options if options else ["Option 1", "Option 2"]
                )
            elif widget_data.type == WidgetType.SLIDER:
                widget = ctk.CTkSlider(
                    widget_frame,
                    width=width,
                    height=height
                )
            elif widget_data.type == WidgetType.PROGRESSBAR:
                widget = ctk.CTkProgressBar(
                    widget_frame,
                    width=width,
                    height=height
                )
            else:
                # Fallback for unknown types
                widget = ctk.CTkLabel(
                    widget_frame,
                    text=f"Unknown widget: {widget_data.type.value}",
                    width=width,
                    height=height
                )
            
            # Pack the widget in its frame
            widget.pack(fill="both", expand=True)
            
            # Place the frame on the canvas at the exact position
            canvas.create_window(
                widget_data.x, widget_data.y,
                window=widget_frame,
                anchor="nw",
                width=width,
                height=height
            )
            
        except Exception as e:
            # Create error indicator if preview fails
            error_frame = ctk.CTkFrame(canvas)
            error_label = ctk.CTkLabel(
                error_frame,
                text=f"Error: {widget_data.type.value}",
                text_color="red"
            )
            error_label.pack()
            canvas.create_window(
                widget_data.x, widget_data.y,
                window=error_frame,
                anchor="nw"
            )
    
    def clear_canvas(self):
        """Clear the canvas"""
        if messagebox.askyesno("Confirm", "Clear all widgets from canvas?"):
            self.canvas.widgets.clear()
            self.canvas.delete("all")
            self.canvas.draw_grid()
            self.canvas.deselect_all()
            self.status_bar.configure(text="Canvas cleared")
    
    def set_theme(self, theme: str):
        """Set the application theme"""
        ctk.set_appearance_mode(theme)
        self.status_bar.configure(text=f"Theme changed to: {theme.title()}")
        self.mode_toggle_button.configure(text=f"🎨 Theme: {theme.title()}")
    
    def set_color_theme(self, color_theme: str):
        """Set the application color theme"""
        ctk.set_default_color_theme(color_theme)
        self.status_bar.configure(text=f"Color theme changed to: {color_theme.title()}")
        self.mode_toggle_button.configure(text=f"🎨 Color: {color_theme.title()}")
    
    def load_recent_files(self):
        """Load recent files from settings"""
        try:
            if os.path.exists("recent_files.json"):
                with open("recent_files.json", 'r') as f:
                    self.recent_files = json.load(f)
        except Exception:
            self.recent_files = []
    
    def save_recent_files(self):
        """Save recent files to settings"""
        try:
            with open("recent_files.json", 'w') as f:
                json.dump(self.recent_files, f)
        except Exception:
            pass
    
    def add_to_recent_files(self, file_path: str):
        """Add file to recent files list"""
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        # Keep only last 10 files
        self.recent_files = self.recent_files[:10]
        self.save_recent_files()
        self.update_recent_menu()
    
    def update_recent_menu(self):
        """Update the recent files menu"""
        self.recent_menu.delete(0, tk.END)
        if self.recent_files:
            for file_path in self.recent_files:
                filename = os.path.basename(file_path)
                self.recent_menu.add_command(
                    label=filename,
                    command=lambda fp=file_path: self.open_recent_file(fp)
                )
        else:
            self.recent_menu.add_command(label="No recent files", state="disabled")
    
    def open_recent_file(self, file_path: str):
        """Open a recent file"""
        if os.path.exists(file_path):
            self.load_project_from_path(file_path)
        else:
            # Remove non-existent file from recent list
            if file_path in self.recent_files:
                self.recent_files.remove(file_path)
                self.save_recent_files()
                self.update_recent_menu()
            messagebox.showerror("Error", f"File not found: {file_path}")
    
    def load_project_from_path(self, file_path: str):
        """Load project from file path with automatic ID cleaning"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Clear current canvas
            self.canvas.widgets.clear()
            self.canvas.delete("all")
            
            # Load window properties if available
            if 'window_properties' in data:
                self.window_properties.update(data['window_properties'])
            
            # Load widgets with automatic ID cleaning
            for widget_data in data.get('widgets', []):
                # Clean the widget ID if it contains hyphens
                original_id = widget_data['id']
                clean_id = CodeGenerator.clean_widget_id(original_id)
                
                widget = WidgetData(
                    id=clean_id,  # Use cleaned ID
                    type=WidgetType(widget_data['type']),
                    x=widget_data['x'],
                    y=widget_data['y'],
                    width=widget_data['width'],
                    height=widget_data['height'],
                    properties={
                        k: WidgetProperty(
                            name=v['name'],
                            value=v['value'],
                            type=v['type'],
                            options=v.get('options')
                        )
                        for k, v in widget_data['properties'].items()
                    }
                )
                self.canvas.widgets[widget.id] = widget
                self.canvas.render_widget(widget)
            
            self.canvas.draw_grid()
            self.current_file = file_path
            self.add_to_recent_files(file_path)
            self.update_status_info()
            
            # Check if any IDs were cleaned and notify user
            cleaned_count = sum(1 for w in data.get('widgets', []) if '-' in w['id'])
            if cleaned_count > 0:
                self.status_bar.configure(text=f"Project loaded: {os.path.basename(file_path)} (cleaned {cleaned_count} widget IDs)")
                messagebox.showinfo("ID Cleaning Applied", 
                    f"Loaded project with automatic ID cleaning:\n"
                    f"✅ {cleaned_count} widget IDs cleaned for valid Python syntax\n"
                    f"✅ All future exports will use clean IDs")
            else:
                self.status_bar.configure(text=f"Project loaded: {os.path.basename(file_path)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load project: {str(e)}")
    
    def update_status_info(self):
        """Update status bar information"""
        widget_count = len(self.canvas.widgets)
        self.widget_count_label.configure(text=f"Widgets: {widget_count}")
        
        if self.current_file:
            filename = os.path.basename(self.current_file)
            self.project_info_label.configure(text=f"Project: {filename}")
        else:
            self.project_info_label.configure(text="No project")
        
        # Reset mode button to default state
        if self.code_editor_frame.winfo_viewable():
            self.mode_toggle_button.configure(text="📝 Code Mode")
        else:
            self.mode_toggle_button.configure(text="🎨 Design Mode")
    
    def show_shortcuts(self):
        """Show keyboard shortcuts dialog"""
        shortcuts_window = ctk.CTkToplevel(self)
        shortcuts_window.title("Keyboard Shortcuts")
        shortcuts_window.geometry("600x400")
        shortcuts_window.transient(self)
        shortcuts_window.grab_set()
        
        # Center the window
        shortcuts_window.update_idletasks()
        x = (shortcuts_window.winfo_screenwidth() // 2) - (600 // 2)
        y = (shortcuts_window.winfo_screenheight() // 2) - (400 // 2)
        shortcuts_window.geometry(f"600x400+{x}+{y}")
        
        # Content
        content_frame = ctk.CTkScrollableFrame(shortcuts_window)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        shortcuts_text = """
FILE OPERATIONS
Ctrl+N          New Project
Ctrl+O          Open Project
Ctrl+S          Save Project
Ctrl+Shift+S    Save Project As
Ctrl+E          Export Python
Alt+F4          Exit

EDIT OPERATIONS
Ctrl+Z          Undo
Ctrl+Y          Redo
Ctrl+C          Copy Widget
Ctrl+V          Paste Widget
Ctrl+X          Cut Widget
Ctrl+D          Duplicate Widget
Ctrl+A          Select All
Delete          Delete Widget

VIEW OPERATIONS
F5              Preview GUI
Ctrl+Shift+V    Toggle Code Editor
Ctrl+G          Toggle Grid
Ctrl+Shift+G    Toggle Grid Snap
Ctrl+B          Toggle Window Boundary
Escape          Clear Selection

CODE EDITOR OPERATIONS
🔄 Sync from Design    Sync code with current design
✅ Validate           Validate code syntax
▶️ Run Code          Run the current code
💾 Export            Export edited code

DESIGN OPERATIONS
Right-click     Context Menu
Drag & Drop     Move Widgets
Resize Handles  Resize Widgets
        """
        
        shortcuts_label = ctk.CTkLabel(
            content_frame,
            text=shortcuts_text,
            font=ctk.CTkFont(family="Consolas", size=12),
            justify="left"
        )
        shortcuts_label.pack(pady=10)
        
        # Close button
        close_button = ctk.CTkButton(
            shortcuts_window,
            text="Close",
            command=shortcuts_window.destroy,
            width=100
        )
        close_button.pack(pady=10)
    
    def show_about(self):
        """Show about dialog"""
        about_window = ctk.CTkToplevel(self)
        about_window.title("About Professional Python GUI Builder")
        about_window.geometry("500x300")
        about_window.transient(self)
        about_window.grab_set()
        
        # Center the window
        about_window.update_idletasks()
        x = (about_window.winfo_screenwidth() // 2) - (500 // 2)
        y = (about_window.winfo_screenheight() // 2) - (300 // 2)
        about_window.geometry(f"500x300+{x}+{y}")
        
        # Content
        content_frame = ctk.CTkFrame(about_window)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            content_frame,
            text="Professional Python GUI Builder",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=10)
        
        # Version
        version_label = ctk.CTkLabel(
            content_frame,
            text="Version 1.0 MVP",
            font=ctk.CTkFont(size=14)
        )
        version_label.pack(pady=5)
        
        # Description
        desc_text = """
A modern, intuitive drag-and-drop interface builder 
for creating CustomTkinter applications.

Features:
• Visual Studio-like interface
• Drag-and-drop widget placement
• Real-time property editing
• Live code generation
• Professional preview system

Built with Python and CustomTkinter
        """
        
        desc_label = ctk.CTkLabel(
            content_frame,
            text=desc_text,
            font=ctk.CTkFont(size=12),
            justify="left"
        )
        desc_label.pack(pady=10)
        
        # Close button
        close_button = ctk.CTkButton(
            about_window,
            text="Close",
            command=about_window.destroy,
            width=100
        )
        close_button.pack(pady=10)
    
    def show_window_properties(self):
        """Show window properties dialog"""
        properties_window = ctk.CTkToplevel(self)
        properties_window.title("Window Properties")
        properties_window.geometry("500x600")
        properties_window.transient(self)
        properties_window.grab_set()
        
        # Center the window
        properties_window.update_idletasks()
        x = (properties_window.winfo_screenwidth() // 2) - (500 // 2)
        y = (properties_window.winfo_screenheight() // 2) - (600 // 2)
        properties_window.geometry(f"500x600+{x}+{y}")
        
        # Content frame
        content_frame = ctk.CTkScrollableFrame(properties_window)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            content_frame,
            text="Window Properties",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=10)
        
        # Window title
        title_frame = ctk.CTkFrame(content_frame)
        title_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(title_frame, text="Window Title:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
        self.title_entry = ctk.CTkEntry(title_frame, width=400)
        self.title_entry.insert(0, self.window_properties['title'])
        self.title_entry.pack(padx=10, pady=5)
        
        # Window size
        size_frame = ctk.CTkFrame(content_frame)
        size_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(size_frame, text="Window Size:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
        
        size_input_frame = ctk.CTkFrame(size_frame)
        size_input_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(size_input_frame, text="Width:").pack(side="left", padx=5)
        self.width_entry = ctk.CTkEntry(size_input_frame, width=80)
        self.width_entry.insert(0, str(self.window_properties['width']))
        self.width_entry.pack(side="left", padx=5)
        
        ctk.CTkLabel(size_input_frame, text="Height:").pack(side="left", padx=5)
        self.height_entry = ctk.CTkEntry(size_input_frame, width=80)
        self.height_entry.insert(0, str(self.window_properties['height']))
        self.height_entry.pack(side="left", padx=5)
        
        # Auto-fit option
        auto_fit_frame = ctk.CTkFrame(content_frame)
        auto_fit_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(auto_fit_frame, text="Auto-fit Options:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
        
        self.auto_fit_checkbox = ctk.CTkCheckBox(
            auto_fit_frame, 
            text="Automatically adjust window size to fit all widgets",
            command=self.on_auto_fit_toggle
        )
        self.auto_fit_checkbox.pack(anchor="w", padx=20, pady=5)
        if self.window_properties.get('auto_fit', True):
            self.auto_fit_checkbox.select()
        
        # Minimum size
        min_size_frame = ctk.CTkFrame(content_frame)
        min_size_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(min_size_frame, text="Minimum Size:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
        
        min_size_input_frame = ctk.CTkFrame(min_size_frame)
        min_size_input_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(min_size_input_frame, text="Min Width:").pack(side="left", padx=5)
        self.min_width_entry = ctk.CTkEntry(min_size_input_frame, width=80)
        self.min_width_entry.insert(0, str(self.window_properties['min_width']))
        self.min_width_entry.pack(side="left", padx=5)
        
        ctk.CTkLabel(min_size_input_frame, text="Min Height:").pack(side="left", padx=5)
        self.min_height_entry = ctk.CTkEntry(min_size_input_frame, width=80)
        self.min_height_entry.insert(0, str(self.window_properties['min_height']))
        self.min_height_entry.pack(side="left", padx=5)
        
        # Window options
        options_frame = ctk.CTkFrame(content_frame)
        options_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(options_frame, text="Window Options:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
        
        self.resizable_checkbox = ctk.CTkCheckBox(
            options_frame, 
            text="Window is resizable"
        )
        self.resizable_checkbox.pack(anchor="w", padx=20, pady=2)
        if self.window_properties['resizable']:
            self.resizable_checkbox.select()
        
        self.center_checkbox = ctk.CTkCheckBox(
            options_frame, 
            text="Center window on screen"
        )
        self.center_checkbox.pack(anchor="w", padx=20, pady=2)
        if self.window_properties['center_on_screen']:
            self.center_checkbox.select()
        
        # Buttons
        button_frame = ctk.CTkFrame(properties_window)
        button_frame.pack(fill="x", padx=20, pady=10)
        
        apply_button = ctk.CTkButton(
            button_frame,
            text="Apply",
            command=lambda: self.apply_window_properties(properties_window),
            width=100
        )
        apply_button.pack(side="left", padx=5)
        
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=properties_window.destroy,
            width=100
        )
        cancel_button.pack(side="left", padx=5)
        
        reset_button = ctk.CTkButton(
            button_frame,
            text="Reset to Defaults",
            command=self.reset_window_properties,
            width=150
        )
        reset_button.pack(side="right", padx=5)
    
    def on_auto_fit_toggle(self):
        """Handle auto-fit toggle"""
        if self.auto_fit_checkbox.get():
            # Enable auto-fit, disable manual size entries
            self.width_entry.configure(state="disabled")
            self.height_entry.configure(state="disabled")
        else:
            # Disable auto-fit, enable manual size entries
            self.width_entry.configure(state="normal")
            self.height_entry.configure(state="normal")
    
    def apply_window_properties(self, window):
        """Apply window properties"""
        try:
            # Update window properties
            self.window_properties['title'] = self.title_entry.get()
            self.window_properties['width'] = int(self.width_entry.get())
            self.window_properties['height'] = int(self.height_entry.get())
            self.window_properties['min_width'] = int(self.min_width_entry.get())
            self.window_properties['min_height'] = int(self.min_height_entry.get())
            self.window_properties['resizable'] = self.resizable_checkbox.get()
            self.window_properties['center_on_screen'] = self.center_checkbox.get()
            self.window_properties['auto_fit'] = self.auto_fit_checkbox.get()
            
            # Mark project as modified
            self.project_modified = True
            self.update_status_info()
            
            self.status_bar.configure(text="Window properties updated")
            window.destroy()
            
        except ValueError as e:
            messagebox.showerror("Invalid Input", f"Please enter valid numbers for size values: {str(e)}")
    
    def reset_window_properties(self):
        """Reset window properties to defaults"""
        self.window_properties = {
            'title': 'Generated GUI',
            'width': 800,
            'height': 600,
            'resizable': True,
            'min_width': 400,
            'min_height': 300,
            'center_on_screen': True,
            'auto_fit': True
        }
        
        # Update the dialog fields
        self.title_entry.delete(0, "end")
        self.title_entry.insert(0, self.window_properties['title'])
        self.width_entry.delete(0, "end")
        self.width_entry.insert(0, str(self.window_properties['width']))
        self.height_entry.delete(0, "end")
        self.height_entry.insert(0, str(self.window_properties['height']))
        self.min_width_entry.delete(0, "end")
        self.min_width_entry.insert(0, str(self.window_properties['min_width']))
        self.min_height_entry.delete(0, "end")
        self.min_height_entry.insert(0, str(self.window_properties['min_height']))
        
        self.resizable_checkbox.select()
        self.center_checkbox.select()
        self.auto_fit_checkbox.select()
        
        self.on_auto_fit_toggle()  # Update entry states
    
    def show_preferences(self):
        """Show preferences window"""
        try:
            # Create and show preferences window
            preferences_window = PreferencesWindow(self, self.prefs_manager)
            
            # Center the window
            preferences_window.update_idletasks()
            x = (preferences_window.winfo_screenwidth() // 2) - (800 // 2)
            y = (preferences_window.winfo_screenheight() // 2) - (600 // 2)
            preferences_window.geometry(f"800x600+{x}+{y}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open preferences: {str(e)}")
    
    def apply_appearance_preferences(self):
        """Apply appearance preferences to the application"""
        try:
            # Set appearance mode
            appearance_mode = self.prefs_manager.get("appearance_mode", "dark")
            ctk.set_appearance_mode(appearance_mode)
            
            # Set color theme
            color_theme = self.prefs_manager.get("color_theme", "blue")
            ctk.set_default_color_theme(color_theme)
            
        except Exception as e:
            print(f"Error applying appearance preferences: {e}")
    
    def apply_window_preferences(self):
        """Apply window preferences to the application"""
        try:
            # Get window preferences
            width = self.prefs_manager.get("window_width", 1400)
            height = self.prefs_manager.get("window_height", 900)
            x = self.prefs_manager.get("window_x", 100)
            y = self.prefs_manager.get("window_y", 100)
            
            # Set window geometry
            if self.prefs_manager.get("remember_window_position", True):
                self.geometry(f"{width}x{height}+{x}+{y}")
            else:
                self.geometry(f"{width}x{height}")
                
        except Exception as e:
            print(f"Error applying window preferences: {e}")
    
    def save_window_preferences(self):
        """Save current window preferences"""
        try:
            if self.prefs_manager.get("remember_window_position", True):
                # Get current window geometry
                geometry = self.geometry()
                # Parse geometry string (e.g., "1400x900+100+200")
                if '+' in geometry:
                    size_pos = geometry.split('+')
                    size = size_pos[0]
                    x = int(size_pos[1])
                    y = int(size_pos[2])
                    width, height = map(int, size.split('x'))
                    
                    # Save window preferences
                    self.prefs_manager.set("window_width", width)
                    self.prefs_manager.set("window_height", height)
                    self.prefs_manager.set("window_x", x)
                    self.prefs_manager.set("window_y", y)
                    
        except Exception as e:
            print(f"Error saving window preferences: {e}")
    
    def on_code_change(self, code: str):
        """Handle code changes in the editor with live canvas updates"""
        print(f"DEBUG: on_code_change called with code length: {len(code)}")
        try:
            # Basic validation - check if code is empty or just comments
            if not code.strip() or code.strip().startswith('#'):
                print("DEBUG: Code is empty or just comments")
                self.status_bar.configure(text="Code editor is empty or contains only comments")
                return
            
            print("DEBUG: Parsing code...")
            # Parse the code to extract widgets and window properties
            widgets, window_properties = CodeParser.parse_code_to_widgets(code)
            print(f"DEBUG: Parsed {len(widgets)} widgets")
            
            # Update window properties if they changed
            if window_properties != self.window_properties:
                self.window_properties.update(window_properties)
            
            # Update canvas with parsed widgets
            if widgets:
                print("DEBUG: Updating canvas with widgets")
                # Clear current canvas
                self.canvas.widgets.clear()
                self.canvas.delete("all")
                
                # Add parsed widgets to canvas
                widget_ids = []
                for widget_data in widgets.values():
                    print(f"DEBUG: Adding widget {widget_data.id} at ({widget_data.x}, {widget_data.y})")
                    self.canvas.widgets[widget_data.id] = widget_data
                    # Force immediate rendering instead of batched
                    self.canvas.render_single_widget(widget_data)
                    widget_ids.append(widget_data.id)
                
                # Redraw grid and update status
                self.canvas.draw_grid()
                self.canvas.draw_window_boundary()
                self.status_bar.configure(text=f"Canvas updated from code - {len(widgets)} widgets")
                
                # Highlight the updated widgets
                self.canvas.highlight_widgets_from_code(widget_ids)
                
                # Mark project as modified
                self.project_modified = True
                self.update_status_info()
                print("DEBUG: Canvas update complete")
            else:
                print("DEBUG: No widgets found in code")
                # No widgets found in code, clear canvas
                if self.canvas.widgets:
                    self.canvas.widgets.clear()
                    self.canvas.delete("all")
                    self.canvas.draw_grid()
                    self.status_bar.configure(text="Canvas cleared - no widgets found in code")
            
        except Exception as e:
            # Handle parsing errors gracefully
            error_msg = f"Error parsing code: {str(e)}"
            print(f"DEBUG: {error_msg}")
            self.status_bar.configure(text="Code parsing error - canvas not updated")
            
            # Show a brief error indicator on the canvas
            self.canvas.delete("code_error_indicator")
            self.canvas.create_text(
                self.canvas.winfo_width() // 2, 30,
                text="⚠️ Code parsing error", fill="#ff4444", 
                font=("Arial", 12, "bold"), tags="code_error_indicator"
            )
            
            # Remove error indicator after 3 seconds
            self.canvas.after(3000, lambda: self.canvas.delete("code_error_indicator"))
    
    def sync_code_from_design(self):
        """Sync code editor with current design"""
        if not self.canvas.widgets:
            self.code_editor.set_code("# No widgets in design yet.\n# Add some widgets to see the generated code here.")
            return
        
        try:
            code = CodeGenerator.generate_code(self.canvas.widgets, self.window_properties)
            self.code_editor.set_code(code)
            self.status_bar.configure(text="Code synced from design")
        except Exception as e:
            error_code = f"# Error generating code: {str(e)}\n# Please check your design and try again."
            self.code_editor.set_code(error_code)
            self.status_bar.configure(text="Error syncing code")
    
    def validate_code(self):
        """Validate the current code in the editor"""
        code = self.code_editor.get_code()
        is_valid, message = CodeGenerator.validate_generated_code(code)
        
        if is_valid:
            self.status_bar.configure(text="Code validation: ✅ Valid")
            messagebox.showinfo("Code Validation", "Code is valid and ready to run!")
        else:
            self.status_bar.configure(text="Code validation: ❌ Invalid")
            messagebox.showerror("Code Validation Error", f"Code has errors:\n{message}")
    
    def run_generated_code(self):
        """Run the current code in the editor"""
        code = self.code_editor.get_code()
        
        # Validate code first
        is_valid, message = CodeGenerator.validate_generated_code(code)
        if not is_valid:
            messagebox.showerror("Code Error", f"Cannot run invalid code:\n{message}")
            return
        
        try:
            # Create a new window to run the code
            exec_window = ctk.CTkToplevel(self)
            exec_window.title("Running Generated Code")
            exec_window.geometry("800x600")
            exec_window.transient(self)
            
            # Center the window
            exec_window.update_idletasks()
            x = (exec_window.winfo_screenwidth() // 2) - (800 // 2)
            y = (exec_window.winfo_screenheight() // 2) - (600 // 2)
            exec_window.geometry(f"800x600+{x}+{y}")
            
            # Execute the code in the new window
            exec_globals = {'ctk': ctk, 'tk': tk}
            exec_locals = {}
            
            # Create a custom exec environment
            exec(code, exec_globals, exec_locals)
            
            # Try to find and run the GeneratedApp
            if 'GeneratedApp' in exec_locals:
                app = exec_locals['GeneratedApp']()
                app.mainloop()
            else:
                messagebox.showinfo("Code Executed", "Code executed successfully, but no GeneratedApp class found.")
            
            self.status_bar.configure(text="Code executed successfully")
            
        except Exception as e:
            error_msg = f"Error running code: {str(e)}"
            self.status_bar.configure(text="Code execution failed")
            messagebox.showerror("Execution Error", error_msg)
    
    def export_edited_code(self):
        """Export the edited code from the editor"""
        code = self.code_editor.get_code()
        
        # Validate code first
        is_valid, message = CodeGenerator.validate_generated_code(code)
        if not is_valid:
            messagebox.showerror("Code Error", f"Cannot export invalid code:\n{message}")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export Edited Code",
            defaultextension=".py",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(code)
                
                self.status_bar.configure(text=f"Edited code exported: {os.path.basename(file_path)}")
                self.mode_toggle_button.configure(text=f"📤 Exported: {os.path.basename(file_path)}")
                messagebox.showinfo("Export Successful", 
                    f"Edited code successfully exported to:\n{file_path}\n\n"
                    f"✅ Code validated and ready to run!")
            except Exception as e:
                error_msg = f"Failed to export edited code: {str(e)}"
                self.status_bar.configure(text="Export failed")
                messagebox.showerror("Export Error", error_msg)

def main():
    """Main entry point"""
    app = GUIBuilderApp()
    app.mainloop()

if __name__ == "__main__":
    main()
