#!/usr/bin/env python3
"""
Widget toolbox component for the GUI Builder application.
"""

import customtkinter as ctk
from models.widget_types import WidgetType


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
