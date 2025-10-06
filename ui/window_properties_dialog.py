#!/usr/bin/env python3
"""
Window properties dialog for the GUI Builder application.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from typing import Dict, Any, Callable

class WindowPropertiesDialog(ctk.CTkToplevel):
    """Dialog for editing window properties of the generated application"""
    
    def __init__(self, parent_app, window_properties: Dict[str, Any], on_apply_callback: Callable):
        super().__init__()
        self.parent_app = parent_app
        self.window_properties = window_properties.copy()
        self.original_properties = window_properties.copy()
        self.on_apply_callback = on_apply_callback
        
        self.title("Window Properties")
        self.geometry("500x600")
        self.minsize(400, 500)
        
        # Make this window modal
        self.transient(parent_app)
        self.grab_set()
        
        # Center the window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.winfo_screenheight() // 2) - (600 // 2)
        self.geometry(f"500x600+{x}+{y}")
        
        self.setup_ui()
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
    
    def setup_ui(self):
        """Setup the window properties dialog UI"""
        # Content frame
        content_frame = ctk.CTkScrollableFrame(self)
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
        self.title_entry.insert(0, self.window_properties.get('title', 'Generated GUI'))
        self.title_entry.pack(padx=10, pady=5)
        
        # Window size
        size_frame = ctk.CTkFrame(content_frame)
        size_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(size_frame, text="Window Size:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
        
        size_input_frame = ctk.CTkFrame(size_frame)
        size_input_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(size_input_frame, text="Width:").pack(side="left", padx=5)
        self.width_entry = ctk.CTkEntry(size_input_frame, width=80)
        self.width_entry.insert(0, str(self.window_properties.get('width', 800)))
        self.width_entry.pack(side="left", padx=5)
        
        ctk.CTkLabel(size_input_frame, text="Height:").pack(side="left", padx=5)
        self.height_entry = ctk.CTkEntry(size_input_frame, width=80)
        self.height_entry.insert(0, str(self.window_properties.get('height', 600)))
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
        self.min_width_entry.insert(0, str(self.window_properties.get('min_width', 400)))
        self.min_width_entry.pack(side="left", padx=5)
        
        ctk.CTkLabel(min_size_input_frame, text="Min Height:").pack(side="left", padx=5)
        self.min_height_entry = ctk.CTkEntry(min_size_input_frame, width=80)
        self.min_height_entry.insert(0, str(self.window_properties.get('min_height', 300)))
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
        if self.window_properties.get('resizable', True):
            self.resizable_checkbox.select()
        
        self.center_checkbox = ctk.CTkCheckBox(
            options_frame, 
            text="Center window on screen"
        )
        self.center_checkbox.pack(anchor="w", padx=20, pady=2)
        if self.window_properties.get('center_on_screen', True):
            self.center_checkbox.select()
        
        # Buttons
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x", padx=20, pady=10)
        
        apply_button = ctk.CTkButton(
            button_frame,
            text="Apply",
            command=self.on_apply,
            width=100
        )
        apply_button.pack(side="left", padx=5)
        
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.on_cancel,
            width=100
        )
        cancel_button.pack(side="left", padx=5)
        
        reset_button = ctk.CTkButton(
            button_frame,
            text="Reset to Defaults",
            command=self.reset_to_defaults,
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
    
    def on_apply(self):
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
            
            # Call the callback to apply changes
            if self.on_apply_callback:
                self.on_apply_callback(self.window_properties)
            
            self.destroy()
            
        except ValueError as e:
            messagebox.showerror("Invalid Input", f"Please enter valid numbers for size values: {str(e)}")
    
    def on_cancel(self):
        """Cancel changes and close dialog"""
        # Restore original properties
        self.window_properties.clear()
        self.window_properties.update(self.original_properties)
        self.destroy()
    
    def reset_to_defaults(self):
        """Reset window properties to defaults"""
        default_properties = {
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
        self.title_entry.insert(0, default_properties['title'])
        self.width_entry.delete(0, "end")
        self.width_entry.insert(0, str(default_properties['width']))
        self.height_entry.delete(0, "end")
        self.height_entry.insert(0, str(default_properties['height']))
        self.min_width_entry.delete(0, "end")
        self.min_width_entry.insert(0, str(default_properties['min_width']))
        self.min_height_entry.delete(0, "end")
        self.min_height_entry.insert(0, str(default_properties['min_height']))
        
        # Update checkboxes
        if default_properties['resizable']:
            self.resizable_checkbox.select()
        else:
            self.resizable_checkbox.deselect()
            
        if default_properties['center_on_screen']:
            self.center_checkbox.select()
        else:
            self.center_checkbox.deselect()
            
        if default_properties['auto_fit']:
            self.auto_fit_checkbox.select()
        else:
            self.auto_fit_checkbox.deselect()
        
        # Update the properties dictionary
        self.window_properties.clear()
        self.window_properties.update(default_properties)
