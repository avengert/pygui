#!/usr/bin/env python3
"""
Design canvas component for the GUI Builder application.
"""

import customtkinter as ctk
import tkinter as tk
import uuid
from typing import Dict, List, Optional, Any
from models.widget_types import WidgetType, WidgetProperty, WidgetData, WidgetGroup


class DesignCanvas(ctk.CTkCanvas):
    """Center panel for designing the GUI"""
    
    def __init__(self, parent, on_widget_select, status_bar=None):
        super().__init__(parent, bg="#2b2b2b", highlightthickness=0)
        self.on_widget_select = on_widget_select
        self.status_bar = status_bar
        self.widgets: Dict[str, WidgetData] = {}
        self.groups: Dict[str, WidgetGroup] = {}
        self.selected_widget_id: Optional[str] = None
        self.selected_widget_ids: List[str] = []  # Multi-selection support
        self.selected_group_id: Optional[str] = None
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
    
    def render_all_widgets(self):
        """Render all widgets on the canvas in layer order"""
        self.delete("all")
        
        # Sort widgets by layer (lower layers first)
        sorted_widgets = sorted(self.widgets.values(), key=lambda w: w.layer)
        
        for widget_data in sorted_widgets:
            self.render_widget(widget_data)
        
        # Render groups after widgets
        for group in self.groups.values():
            self.render_group(group)
        
        self.draw_grid()
    
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
        if widget_data.id in self.selected_widget_ids:
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
        
        # Selection handles (for all selected widgets)
        if widget_data.id in self.selected_widget_ids:
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
        
        # First check if clicking on a group
        group_id = self.find_group_at_position(event.x, event.y)
        if group_id:
            self.select_group(group_id)
            self.deselect_all()
            # Set drag data for group movement
            group = self.groups[group_id]
            self.drag_data = {
                "x": event.x, 
                "y": event.y, 
                "widget": None,
                "group": group_id,
                "mode": "move_group",
                "original_x": group.x,
                "original_y": group.y
            }
            return "break"
        
        # Then check if clicking on a resize handle
        handle_info = self.find_handle_at_position(event.x, event.y)
        if handle_info:
            item_id, handle_index, item_type = handle_info
            
            if item_type == "group_props":
                # Open group properties dialog
                self.show_group_properties_dialog(item_id)
                return "break"
            elif item_type == "group":
                # Group resize
                group = self.groups[item_id]
                self.drag_data = {
                    "x": event.x, 
                    "y": event.y, 
                    "group": item_id,
                    "mode": "resize_group", 
                    "handle": handle_index,
                    "original_x": group.x,
                    "original_y": group.y,
                    "original_width": group.width,
                    "original_height": group.height
                }
                return "break"
            elif item_type == "widget":
                # Widget resize
                self.select_widget(item_id)
                widget_data = self.widgets[item_id]
                self.drag_data = {
                    "x": event.x, 
                    "y": event.y, 
                    "widget": item_id, 
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
            # Check for Ctrl+click for multi-selection
            if event.state & 0x4:  # Ctrl key is pressed
                self.toggle_widget_selection(widget_id)
            else:
                self.select_widget(widget_id)
                self.deselect_group()
            
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
            self.deselect_group()
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
        # Check group handles first
        if self.selected_group_id and self.selected_group_id in self.groups:
            group = self.groups[self.selected_group_id]
            handle_size = 8
            
            # Check group handles
            handles = [
                (group.x - 5 - handle_size//2, group.y - 5 - handle_size//2),  # Top-left
                (group.x + group.width + 5 - handle_size//2, group.y - 5 - handle_size//2),  # Top-right
                (group.x - 5 - handle_size//2, group.y + group.height + 5 - handle_size//2),  # Bottom-left
                (group.x + group.width + 5 - handle_size//2, group.y + group.height + 5 - handle_size//2),  # Bottom-right
            ]
            
            for i, (hx, hy) in enumerate(handles):
                if (hx <= x <= hx + handle_size and hy <= y <= hy + handle_size):
                    return (self.selected_group_id, i, "group")
            
            # Check group properties button
            props_x = group.x + group.width - 80
            props_y = group.y - 25
            if (props_x <= x <= props_x + 70 and props_y <= y <= props_y + 15):
                return (self.selected_group_id, -1, "group_props")
        
        # Check widget handles
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
                return (self.selected_widget_id, i, "widget")
        return None
    
    def select_widget(self, widget_id: str):
        """Select a widget"""
        self.selected_widget_id = widget_id
        self.selected_widget_ids = [widget_id]  # Update multi-selection
        self.on_widget_select(self.widgets[widget_id])
        self.render_widget(self.widgets[widget_id])
    
    def toggle_widget_selection(self, widget_id: str):
        """Toggle widget selection for multi-selection"""
        if widget_id in self.selected_widget_ids:
            # Remove from selection
            self.selected_widget_ids.remove(widget_id)
            if self.selected_widget_id == widget_id:
                # If this was the primary selection, pick another or clear
                if self.selected_widget_ids:
                    self.selected_widget_id = self.selected_widget_ids[0]
                    self.on_widget_select(self.widgets[self.selected_widget_id])
                else:
                    self.selected_widget_id = None
                    self.on_widget_select(None)
        else:
            # Add to selection
            self.selected_widget_ids.append(widget_id)
            self.selected_widget_id = widget_id
            self.on_widget_select(self.widgets[widget_id])
        
        # Re-render all widgets to show selection state
        for widget_data in self.widgets.values():
            self.render_widget(widget_data)
    
    def deselect_all(self):
        """Deselect all widgets"""
        self.selected_widget_id = None
        self.selected_widget_ids = []
        self.on_widget_select(None)
        for widget_data in self.widgets.values():
            self.render_widget(widget_data)
    
    def on_canvas_drag(self, event):
        """Handle canvas drag events"""
        if self.drag_data.get("group"):
            group_id = self.drag_data["group"]
            mode = self.drag_data.get("mode", "move_group")
            
            if mode == "move_group":
                # Handle group movement
                if group_id in self.groups:
                    group = self.groups[group_id]
                    original_x = self.drag_data.get("original_x", group.x)
                    original_y = self.drag_data.get("original_y", group.y)
                    
                    dx = event.x - self.drag_data["x"]
                    dy = event.y - self.drag_data["y"]
                    
                    # Snap to grid if enabled
                    if self.snap_to_grid:
                        dx = round(dx / self.grid_size) * self.grid_size
                        dy = round(dy / self.grid_size) * self.grid_size
                    
                    # Move the group
                    self.move_group(group_id, dx, dy)
                    
                    # Update drag data for next movement
                    self.drag_data["x"] = event.x
                    self.drag_data["y"] = event.y
                    self.drag_data["original_x"] = group.x
                    self.drag_data["original_y"] = group.y
                    
            elif mode == "resize_group":
                # Handle group resizing
                if group_id in self.groups:
                    group = self.groups[group_id]
                    handle_index = self.drag_data["handle"]
                    
                    # Get original group dimensions
                    original_x = self.drag_data.get("original_x", group.x)
                    original_y = self.drag_data.get("original_y", group.y)
                    original_width = self.drag_data.get("original_width", group.width)
                    original_height = self.drag_data.get("original_height", group.height)
                    
                    # Calculate new dimensions based on handle
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
                    new_width = max(50, new_width)
                    new_height = max(50, new_height)
                    
                    # Snap to grid if enabled
                    if self.snap_to_grid:
                        new_x = round(new_x / self.grid_size) * self.grid_size
                        new_y = round(new_y / self.grid_size) * self.grid_size
                        new_width = round(new_width / self.grid_size) * self.grid_size
                        new_height = round(new_height / self.grid_size) * self.grid_size
                    
                    # Resize the group
                    self.resize_group(group_id, new_width, new_height)
                
        elif self.drag_data["widget"]:
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
        # Check for group first
        group_id = self.find_group_at_position(event.x, event.y)
        if group_id:
            self.show_group_context_menu(event.x, event.y, group_id)
            return
        
        # Then check for widget
        widget_id = self.find_widget_at_position(event.x, event.y)
        if widget_id:
            self.show_context_menu(event.x, event.y, widget_id)
    
    def show_context_menu(self, x: int, y: int, widget_id: str):
        """Show context menu for widget"""
        context_menu = tk.Menu(self, tearoff=0)
        context_menu.add_command(label="Delete", command=lambda: self.delete_widget(widget_id))
        context_menu.add_command(label="Duplicate", command=lambda: self.duplicate_widget(widget_id))
        context_menu.add_separator()
        context_menu.add_command(label="Bring to Front", command=lambda: self.bring_to_front(widget_id))
        context_menu.add_command(label="Send to Back", command=lambda: self.send_to_back(widget_id))
        context_menu.add_separator()
        
        # Grouping options
        if widget_id in self.widgets:
            widget = self.widgets[widget_id]
            if widget.group_id:
                # Widget is in a group
                context_menu.add_command(label="Remove from Group", command=lambda: self.remove_from_group(widget_id, widget.group_id))
                context_menu.add_command(label="Ungroup All", command=lambda: self.ungroup_widgets(widget.group_id))
            else:
                # Widget is not in a group
                context_menu.add_command(label="Create Group", command=lambda: self.create_group_from_selection())
                
                # Add to Group submenu
                if self.groups:
                    add_to_group_menu = tk.Menu(context_menu, tearoff=0)
                    for group_id, group in self.groups.items():
                        add_to_group_menu.add_command(
                            label=f"{group.name} ({len(group.widget_ids)} widgets)",
                            command=lambda gid=group_id: self.add_to_group(widget_id, gid)
                        )
                    context_menu.add_cascade(label="Add to Group", menu=add_to_group_menu)
                else:
                    context_menu.add_command(label="Add to Group", state="disabled")
        
        try:
            context_menu.tk_popup(x, y)
        finally:
            context_menu.grab_release()
    
    def show_group_context_menu(self, x: int, y: int, group_id: str):
        """Show context menu for group"""
        context_menu = tk.Menu(self, tearoff=0)
        context_menu.add_command(label="Properties", command=lambda: self.show_group_properties_dialog(group_id))
        context_menu.add_separator()
        
        # Add widget to group submenu
        add_widget_menu = tk.Menu(context_menu, tearoff=0)
        available_widgets = []
        for widget_id, widget in self.widgets.items():
            if widget_id not in self.groups[group_id].widget_ids:
                available_widgets.append((widget_id, widget))
        
        if available_widgets:
            for widget_id, widget in available_widgets[:10]:  # Limit to 10 items
                add_widget_menu.add_command(
                    label=f"{widget.type.value} ({widget_id[:8]})",
                    command=lambda wid=widget_id: self.add_to_group(wid, group_id)
                )
            if len(available_widgets) > 10:
                add_widget_menu.add_command(label="... (more available)", state="disabled")
            context_menu.add_cascade(label="Add Widget", menu=add_widget_menu)
        else:
            context_menu.add_command(label="Add Widget", state="disabled")
        
        context_menu.add_separator()
        context_menu.add_command(label="Ungroup", command=lambda: self.ungroup_widgets(group_id))
        context_menu.add_command(label="Delete Group", command=lambda: self.delete_group(group_id))
        context_menu.add_separator()
        context_menu.add_command(label="Bring to Front", command=lambda: self.bring_group_to_front(group_id))
        context_menu.add_command(label="Send to Back", command=lambda: self.send_group_to_back(group_id))
        
        try:
            context_menu.tk_popup(x, y)
        finally:
            context_menu.grab_release()
    
    def create_group_from_selection(self):
        """Create a group from currently selected widgets"""
        if len(self.selected_widget_ids) >= 2:
            self.create_group(name="New Group")
        else:
            if self.status_bar:
                self.status_bar.configure(text="Select at least 2 widgets to create a group (Ctrl+click for multi-selection)")
    
    
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
            # Select all widgets
            self.selected_widget_ids = list(self.widgets.keys())
            self.selected_widget_id = self.selected_widget_ids[0] if self.selected_widget_ids else None
            self.on_widget_select(self.widgets[self.selected_widget_id] if self.selected_widget_id else None)
            
            # Re-render all widgets to show selection
            for widget_data in self.widgets.values():
                self.render_widget(widget_data)
            
            if self.status_bar:
                self.status_bar.configure(text=f"Selected {len(self.selected_widget_ids)} widgets")
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
    
    # Widget Grouping and Layer Management Methods
    
    def create_group(self, widget_ids: List[str] = None, name: str = None) -> str:
        """Create a group from selected widgets"""
        # Use multi-selection if no widget_ids provided
        if widget_ids is None:
            widget_ids = self.selected_widget_ids.copy()
        
        if len(widget_ids) < 2:
            return None
        
        # Calculate group bounds
        min_x = min(self.widgets[wid].x for wid in widget_ids)
        min_y = min(self.widgets[wid].y for wid in widget_ids)
        max_x = max(self.widgets[wid].x + self.widgets[wid].width for wid in widget_ids)
        max_y = max(self.widgets[wid].y + self.widgets[wid].height for wid in widget_ids)
        
        group_id = str(uuid.uuid4())
        group_name = name or f"Group {len(self.groups) + 1}"
        
        # If no name provided, ask user for a name
        if not name:
            from tkinter import simpledialog
            group_name = simpledialog.askstring("Group Name", "Enter group name:", initialvalue=group_name)
            if not group_name:
                group_name = f"Group {len(self.groups) + 1}"
        
        group = WidgetGroup(
            id=group_id,
            name=group_name,
            widget_ids=widget_ids.copy(),
            x=min_x,
            y=min_y,
            width=max_x - min_x,
            height=max_y - min_y
        )
        
        self.groups[group_id] = group
        
        # Assign widgets to group
        for widget_id in widget_ids:
            if widget_id in self.widgets:
                self.widgets[widget_id].group_id = group_id
        
        # Render group outline
        self.render_group(group)
        
        if self.status_bar:
            self.status_bar.configure(text=f"Group '{group_name}' created with {len(widget_ids)} widgets")
        
        return group_id
    
    def ungroup_widgets(self, group_id: str):
        """Ungroup widgets from a group"""
        if group_id not in self.groups:
            return
        
        group = self.groups[group_id]
        
        # Remove group assignment from widgets and re-render them
        for widget_id in group.widget_ids:
            if widget_id in self.widgets:
                self.widgets[widget_id].group_id = None
                # Re-render widget to restore individual functionality
                self.render_widget(self.widgets[widget_id])
                # Ensure widget is properly set up for individual interaction
                self.delete(f"widget_{widget_id}")  # Remove old rendering
                self.render_widget(self.widgets[widget_id])  # Fresh render
        
        # Remove group
        del self.groups[group_id]
        self.delete(f"group_{group_id}")
        
        # Clear any group selection
        if self.selected_group_id == group_id:
            self.selected_group_id = None
        
        if self.status_bar:
            self.status_bar.configure(text=f"Group '{group.name}' ungrouped - widgets restored to individual mode")
    
    def add_to_group(self, widget_id: str, group_id: str):
        """Add a widget to an existing group"""
        if widget_id not in self.widgets or group_id not in self.groups:
            return
        
        # Remove from current group if any
        if self.widgets[widget_id].group_id:
            self.remove_from_group(widget_id, self.widgets[widget_id].group_id)
        
        # Add to new group
        self.widgets[widget_id].group_id = group_id
        self.groups[group_id].widget_ids.append(widget_id)
        
        # Update group bounds
        self.update_group_bounds(group_id)
        self.render_group(self.groups[group_id])
        
        # Show status feedback
        if self.status_bar:
            self.status_bar.configure(text=f"Widget added to group '{self.groups[group_id].name}'")
    
    def remove_from_group(self, widget_id: str, group_id: str):
        """Remove a widget from a group"""
        if widget_id not in self.widgets or group_id not in self.groups:
            return
        
        # Remove from group
        if widget_id in self.groups[group_id].widget_ids:
            self.groups[group_id].widget_ids.remove(widget_id)
        
        # Remove group assignment
        self.widgets[widget_id].group_id = None
        
        # Re-render widget to restore individual functionality
        self.delete(f"widget_{widget_id}")  # Remove old rendering
        self.render_widget(self.widgets[widget_id])  # Fresh render
        
        # Update group bounds
        self.update_group_bounds(group_id)
        self.render_group(self.groups[group_id])
        
        # Show status feedback
        if self.status_bar:
            self.status_bar.configure(text=f"Widget removed from group '{self.groups[group_id].name}'")
    
    def update_group_bounds(self, group_id: str):
        """Update group bounds based on its widgets"""
        if group_id not in self.groups:
            return
        
        group = self.groups[group_id]
        if not group.widget_ids:
            return
        
        # Calculate new bounds
        min_x = min(self.widgets[wid].x for wid in group.widget_ids if wid in self.widgets)
        min_y = min(self.widgets[wid].y for wid in group.widget_ids if wid in self.widgets)
        max_x = max(self.widgets[wid].x + self.widgets[wid].width for wid in group.widget_ids if wid in self.widgets)
        max_y = max(self.widgets[wid].y + self.widgets[wid].height for wid in group.widget_ids if wid in self.widgets)
        
        group.x = min_x
        group.y = min_y
        group.width = max_x - min_x
        group.height = max_y - min_y
    
    def render_group(self, group: WidgetGroup):
        """Render group outline and controls"""
        if not group.visible:
            return
        
        # Remove existing group representation
        self.delete(f"group_{group.id}")
        
        # Draw group outline
        self.create_rectangle(
            group.x - 5, group.y - 5,
            group.x + group.width + 5, group.y + group.height + 5,
            outline="#ffaa00",  # Orange outline
            width=2,
            dash=(5, 5),  # Dashed line
            tags=f"group_{group.id}"
        )
        
        # Add group label
        self.create_text(
            group.x, group.y - 15,
            text=f"📁 {group.name}",
            fill="#ffaa00",
            font=("Arial", 10, "bold"),
            anchor="w",
            tags=f"group_{group.id}"
        )
        
        # Add group controls if selected
        if group.id == self.selected_group_id:
            self.draw_group_controls(group)
    
    def draw_group_controls(self, group: WidgetGroup):
        """Draw group control handles"""
        # Corner handles for group resizing
        handle_size = 8
        handles = [
            (group.x - 5 - handle_size//2, group.y - 5 - handle_size//2),  # Top-left
            (group.x + group.width + 5 - handle_size//2, group.y - 5 - handle_size//2),  # Top-right
            (group.x - 5 - handle_size//2, group.y + group.height + 5 - handle_size//2),  # Bottom-left
            (group.x + group.width + 5 - handle_size//2, group.y + group.height + 5 - handle_size//2),  # Bottom-right
        ]
        
        for i, (hx, hy) in enumerate(handles):
            self.create_rectangle(
                hx, hy, hx + handle_size, hy + handle_size,
                fill="#ffaa00",
                outline="#ffffff",
                width=2,
                tags=f"group_{group.id}"
            )
        
        # Add group properties button
        props_x = group.x + group.width - 80
        props_y = group.y - 25
        self.create_rectangle(
            props_x, props_y, props_x + 70, props_y + 15,
            fill="#ffaa00",
            outline="#ffffff",
            width=1,
            tags=f"group_{group.id}"
        )
        self.create_text(
            props_x + 35, props_y + 7,
            text="⚙️ Props",
            fill="#ffffff",
            font=("Arial", 8, "bold"),
            tags=f"group_{group.id}"
        )
    
    def move_group(self, group_id: str, dx: int, dy: int):
        """Move all widgets in a group"""
        if group_id not in self.groups:
            return
        
        group = self.groups[group_id]
        
        # Move all widgets in the group
        for widget_id in group.widget_ids:
            if widget_id in self.widgets:
                widget = self.widgets[widget_id]
                widget.x += dx
                widget.y += dy
                self.render_widget(widget)
        
        # Update group bounds
        self.update_group_bounds(group_id)
        self.render_group(group)
    
    def resize_group(self, group_id: str, new_width: int, new_height: int):
        """Resize all widgets in a group proportionally"""
        if group_id not in self.groups:
            return
        
        group = self.groups[group_id]
        
        # Calculate scale factors
        scale_x = new_width / group.width if group.width > 0 else 1
        scale_y = new_height / group.height if group.height > 0 else 1
        
        # Resize all widgets in the group
        for widget_id in group.widget_ids:
            if widget_id in self.widgets:
                widget = self.widgets[widget_id]
                # Calculate relative position within group
                rel_x = widget.x - group.x
                rel_y = widget.y - group.y
                
                # Apply scaling
                widget.x = group.x + int(rel_x * scale_x)
                widget.y = group.y + int(rel_y * scale_y)
                widget.width = max(20, int(widget.width * scale_x))
                widget.height = max(20, int(widget.height * scale_y))
                
                self.render_widget(widget)
        
        # Update group bounds
        group.width = new_width
        group.height = new_height
        self.render_group(group)
    
    def delete_group(self, group_id: str):
        """Delete a group and all its widgets"""
        if group_id not in self.groups:
            return
        
        group = self.groups[group_id]
        
        # Delete all widgets in the group
        for widget_id in group.widget_ids:
            if widget_id in self.widgets:
                self.delete_widget(widget_id)
        
        # Remove group
        del self.groups[group_id]
        self.delete(f"group_{group_id}")
        
        if self.status_bar:
            self.status_bar.configure(text=f"Group '{group.name}' deleted")
    
    def set_widget_layer(self, widget_id: str, layer: int):
        """Set the layer of a widget"""
        if widget_id in self.widgets:
            self.widgets[widget_id].layer = layer
            self.render_widget(self.widgets[widget_id])
    
    def set_group_layer(self, group_id: str, layer: int):
        """Set the layer of all widgets in a group"""
        if group_id not in self.groups:
            return
        
        group = self.groups[group_id]
        group.layer = layer
        
        for widget_id in group.widget_ids:
            if widget_id in self.widgets:
                self.widgets[widget_id].layer = layer
                self.render_widget(self.widgets[widget_id])
        
        self.render_group(group)
    
    def bring_to_front(self, widget_id: str):
        """Bring widget to front (highest layer)"""
        if widget_id in self.widgets:
            max_layer = max((w.layer for w in self.widgets.values()), default=0)
            self.set_widget_layer(widget_id, max_layer + 1)
    
    def send_to_back(self, widget_id: str):
        """Send widget to back (lowest layer)"""
        if widget_id in self.widgets:
            min_layer = min((w.layer for w in self.widgets.values()), default=0)
            self.set_widget_layer(widget_id, min_layer - 1)
    
    def bring_group_to_front(self, group_id: str):
        """Bring group to front (highest layer)"""
        if group_id in self.groups:
            max_layer = max((w.layer for w in self.widgets.values()), default=0)
            self.set_group_layer(group_id, max_layer + 1)
            if self.status_bar:
                self.status_bar.configure(text="Group brought to front")
    
    def send_group_to_back(self, group_id: str):
        """Send group to back (lowest layer)"""
        if group_id in self.groups:
            min_layer = min((w.layer for w in self.widgets.values()), default=0)
            self.set_group_layer(group_id, min_layer - 1)
            if self.status_bar:
                self.status_bar.configure(text="Group sent to back")
    
    def find_group_at_position(self, x: int, y: int) -> Optional[str]:
        """Find group at given position"""
        for group_id, group in self.groups.items():
            if (group.x - 5 <= x <= group.x + group.width + 5 and
                group.y - 5 <= y <= group.y + group.height + 5):
                return group_id
        return None
    
    def select_group(self, group_id: str):
        """Select a group"""
        self.selected_group_id = group_id
        self.selected_widget_id = None
        self.render_group(self.groups[group_id])
        
        if self.status_bar:
            self.status_bar.configure(text=f"Selected group: {self.groups[group_id].name}")
    
    def deselect_group(self):
        """Deselect current group"""
        if self.selected_group_id:
            self.render_group(self.groups[self.selected_group_id])
        self.selected_group_id = None
    
    def show_group_properties_dialog(self, group_id: str):
        """Show group properties dialog"""
        if group_id in self.groups:
            from ui import GroupPropertiesDialog
            GroupPropertiesDialog(
                self.winfo_toplevel(),
                self.groups[group_id],
                self.on_group_properties_update
            )
    
    def on_group_properties_update(self, group: WidgetGroup):
        """Handle group properties update"""
        # Update group layer for all widgets
        for widget_id in group.widget_ids:
            if widget_id in self.widgets:
                self.widgets[widget_id].layer = group.layer
                self.render_widget(self.widgets[widget_id])
        
        # Re-render group with updated properties
        self.render_group(group)
        
        # Update layer list if visible
        main_app = self.winfo_toplevel()
        if hasattr(main_app, 'layer_panel_frame') and main_app.layer_panel_frame.winfo_viewable():
            main_app.update_layer_list()
        
        if self.status_bar:
            self.status_bar.configure(text=f"Group '{group.name}' properties updated")
