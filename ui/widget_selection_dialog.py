#!/usr/bin/env python3
"""
Widget selection dialog for adding widgets to groups.
"""

import customtkinter as ctk
import tkinter as tk
from typing import List, Optional, Callable
from models.widget_types import WidgetData


class WidgetSelectionDialog(ctk.CTkToplevel):
    """Dialog for selecting widgets to add to a group"""
    
    def __init__(self, parent, available_widgets: List[WidgetData], on_widget_selected: Callable[[str], None]):
        super().__init__(parent)
        
        self.available_widgets = available_widgets
        self.on_widget_selected = on_widget_selected
        self.selected_widget_id = None
        
        self.title("Add Widget to Group")
        self.geometry("500x400")
        self.resizable(False, False)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Center the dialog
        self.center_dialog()
        
        self.setup_ui()
    
    def center_dialog(self):
        """Center the dialog on the parent window"""
        self.update_idletasks()
        parent_x = self.master.winfo_x()
        parent_y = self.master.winfo_y()
        parent_width = self.master.winfo_width()
        parent_height = self.master.winfo_height()
        
        x = parent_x + (parent_width // 2) - (500 // 2)
        y = parent_y + (parent_height // 2) - (400 // 2)
        
        self.geometry(f"500x400+{x}+{y}")
    
    def setup_ui(self):
        """Setup the dialog UI"""
        # Main frame
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame, 
            text="Select Widget to Add", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Widget list
        self.widget_list_frame = ctk.CTkScrollableFrame(main_frame, height=250)
        self.widget_list_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Create widget items
        self.widget_items = []
        for widget in self.available_widgets:
            self.create_widget_item(widget)
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x")
        
        cancel_btn = ctk.CTkButton(button_frame, text="Cancel", command=self.cancel, width=100)
        cancel_btn.pack(side="right", padx=(10, 0))
        
        add_btn = ctk.CTkButton(button_frame, text="Add Widget", command=self.add_widget, width=120)
        add_btn.pack(side="right")
    
    def create_widget_item(self, widget: WidgetData):
        """Create a widget item in the list"""
        widget_frame = ctk.CTkFrame(self.widget_list_frame)
        widget_frame.pack(fill="x", padx=5, pady=2)
        
        # Widget info
        widget_text = f"{widget.type.value} - ID: {widget.id[:8]}"
        widget_label = ctk.CTkLabel(widget_frame, text=widget_text, font=ctk.CTkFont(size=12))
        widget_label.pack(side="left", padx=10, pady=5)
        
        # Position info
        pos_text = f"({widget.x}, {widget.y}) {widget.width}×{widget.height}"
        pos_label = ctk.CTkLabel(widget_frame, text=pos_text, font=ctk.CTkFont(size=10), text_color="gray")
        pos_label.pack(side="left", padx=10, pady=5)
        
        # Select button
        select_btn = ctk.CTkButton(
            widget_frame, 
            text="Select", 
            width=80,
            command=lambda wid=widget.id: self.select_widget(wid)
        )
        select_btn.pack(side="right", padx=10, pady=5)
        
        self.widget_items.append((widget.id, widget_frame, select_btn))
    
    def select_widget(self, widget_id: str):
        """Select a widget"""
        self.selected_widget_id = widget_id
        
        # Update visual selection
        for wid, frame, btn in self.widget_items:
            if wid == widget_id:
                frame.configure(fg_color=("#3B8ED0", "#1F6AA5"))  # Blue selection
                btn.configure(text="Selected", fg_color=("#2FA572", "#0F5132"))  # Green
            else:
                frame.configure(fg_color=("gray90", "gray25"))  # Default
                btn.configure(text="Select", fg_color=("#3B8ED0", "#1F6AA5"))  # Blue
    
    def add_widget(self):
        """Add selected widget to group"""
        if self.selected_widget_id:
            self.on_widget_selected(self.selected_widget_id)
            self.destroy()
        else:
            from tkinter import messagebox
            messagebox.showwarning("No Selection", "Please select a widget to add.")
    
    def cancel(self):
        """Cancel and close dialog"""
        self.destroy()
