#!/usr/bin/env python3
"""
Properties editor component for the GUI Builder application.
"""

import customtkinter as ctk
from typing import Dict, Optional
from models.widget_types import WidgetData, WidgetProperty


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
