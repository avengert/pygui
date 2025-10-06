#!/usr/bin/env python3
"""
Group properties dialog for the GUI Builder application.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from typing import Optional, Callable
from models.widget_types import WidgetGroup


class GroupPropertiesDialog(ctk.CTkToplevel):
    """Dialog for editing group properties"""
    
    def __init__(self, parent, group: WidgetGroup, on_group_update: Callable[[WidgetGroup], None]):
        super().__init__(parent)
        
        self.group = group
        self.on_group_update = on_group_update
        
        self.title(f"Group Properties - {group.name}")
        self.geometry("400x300")
        self.resizable(False, False)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Center the dialog
        self.center_dialog()
        
        self.setup_ui()
        
        # Focus on name entry
        self.name_entry.focus()
        self.name_entry.select_range(0, tk.END)
    
    def center_dialog(self):
        """Center the dialog on the parent window"""
        self.update_idletasks()
        parent_x = self.master.winfo_x()
        parent_y = self.master.winfo_y()
        parent_width = self.master.winfo_width()
        parent_height = self.master.winfo_height()
        
        x = parent_x + (parent_width // 2) - (400 // 2)
        y = parent_y + (parent_height // 2) - (300 // 2)
        
        self.geometry(f"400x300+{x}+{y}")
    
    def setup_ui(self):
        """Setup the dialog UI"""
        # Main frame
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame, 
            text="Group Properties", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Group name
        name_frame = ctk.CTkFrame(main_frame)
        name_frame.pack(fill="x", pady=(0, 15))
        
        name_label = ctk.CTkLabel(name_frame, text="Group Name:", font=ctk.CTkFont(weight="bold"))
        name_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.name_entry = ctk.CTkEntry(name_frame, placeholder_text="Enter group name...")
        self.name_entry.pack(fill="x", padx=10, pady=(0, 10))
        self.name_entry.insert(0, self.group.name)
        
        # Group info
        info_frame = ctk.CTkFrame(main_frame)
        info_frame.pack(fill="x", pady=(0, 15))
        
        info_label = ctk.CTkLabel(info_frame, text="Group Information:", font=ctk.CTkFont(weight="bold"))
        info_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Widget count
        self.widget_count = len(self.group.widget_ids)
        self.count_label = ctk.CTkLabel(info_frame, text=f"Widgets: {self.widget_count}")
        self.count_label.pack(anchor="w", padx=10, pady=(0, 5))
        
        # Dimensions
        dim_label = ctk.CTkLabel(info_frame, text=f"Size: {self.group.width} × {self.group.height}")
        dim_label.pack(anchor="w", padx=10, pady=(0, 5))
        
        # Position
        pos_label = ctk.CTkLabel(info_frame, text=f"Position: ({self.group.x}, {self.group.y})")
        pos_label.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Widget management
        widget_frame = ctk.CTkFrame(main_frame)
        widget_frame.pack(fill="x", pady=(0, 15))
        
        widget_label = ctk.CTkLabel(widget_frame, text="Widget Management:", font=ctk.CTkFont(weight="bold"))
        widget_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Widget list
        self.widget_list_frame = ctk.CTkScrollableFrame(widget_frame, height=120)
        self.widget_list_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.update_widget_list()
        
        # Widget management buttons
        widget_buttons = ctk.CTkFrame(widget_frame)
        widget_buttons.pack(fill="x", padx=10, pady=(0, 10))
        
        add_btn = ctk.CTkButton(widget_buttons, text="+ Add Widget", command=self.add_widget_to_group, width=100)
        add_btn.pack(side="left", padx=(0, 5))
        
        remove_btn = ctk.CTkButton(widget_buttons, text="- Remove", command=self.remove_selected_widget, width=100)
        remove_btn.pack(side="left", padx=(0, 5))
        
        refresh_btn = ctk.CTkButton(widget_buttons, text="🔄 Refresh", command=self.update_widget_list, width=80)
        refresh_btn.pack(side="left")
        
        # Layer controls
        layer_frame = ctk.CTkFrame(main_frame)
        layer_frame.pack(fill="x", pady=(0, 20))
        
        layer_label = ctk.CTkLabel(layer_frame, text="Layer:", font=ctk.CTkFont(weight="bold"))
        layer_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        layer_controls = ctk.CTkFrame(layer_frame)
        layer_controls.pack(fill="x", padx=10, pady=(0, 10))
        
        self.layer_var = ctk.StringVar(value=str(self.group.layer))
        self.layer_entry = ctk.CTkEntry(layer_controls, textvariable=self.layer_var, width=100)
        self.layer_entry.pack(side="left", padx=(0, 10))
        
        layer_up_btn = ctk.CTkButton(layer_controls, text="↑", width=30, command=self.layer_up)
        layer_up_btn.pack(side="left", padx=(0, 5))
        
        layer_down_btn = ctk.CTkButton(layer_controls, text="↓", width=30, command=self.layer_down)
        layer_down_btn.pack(side="left")
        
        # Visibility and lock controls
        controls_frame = ctk.CTkFrame(main_frame)
        controls_frame.pack(fill="x", pady=(0, 20))
        
        self.visible_var = ctk.BooleanVar(value=self.group.visible)
        visible_check = ctk.CTkCheckBox(controls_frame, text="Visible", variable=self.visible_var)
        visible_check.pack(anchor="w", padx=10, pady=10)
        
        self.locked_var = ctk.BooleanVar(value=self.group.locked)
        locked_check = ctk.CTkCheckBox(controls_frame, text="Locked", variable=self.locked_var)
        locked_check.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x")
        
        cancel_btn = ctk.CTkButton(button_frame, text="Cancel", command=self.cancel, width=100)
        cancel_btn.pack(side="right", padx=(10, 0))
        
        ok_btn = ctk.CTkButton(button_frame, text="OK", command=self.ok, width=100)
        ok_btn.pack(side="right")
    
    def layer_up(self):
        """Move layer up"""
        try:
            current_layer = int(self.layer_var.get())
            self.layer_var.set(str(current_layer + 1))
        except ValueError:
            self.layer_var.set("0")
    
    def layer_down(self):
        """Move layer down"""
        try:
            current_layer = int(self.layer_var.get())
            self.layer_var.set(str(current_layer - 1))
        except ValueError:
            self.layer_var.set("0")
    
    def update_widget_list(self):
        """Update the widget list display"""
        # Clear existing widgets
        for widget in self.widget_list_frame.winfo_children():
            widget.destroy()
        
        # Get canvas reference
        canvas = self.master.canvas if hasattr(self.master, 'canvas') else None
        if not canvas:
            return
        
        # Display widgets in group
        for i, widget_id in enumerate(self.group.widget_ids):
            if widget_id in canvas.widgets:
                widget = canvas.widgets[widget_id]
                widget_frame = ctk.CTkFrame(self.widget_list_frame)
                widget_frame.pack(fill="x", padx=2, pady=1)
                
                # Widget info
                widget_text = f"{widget.type.value} ({widget_id[:8]})"
                widget_label = ctk.CTkLabel(widget_frame, text=widget_text, font=ctk.CTkFont(size=10))
                widget_label.pack(side="left", padx=5, pady=2)
                
                # Remove button
                remove_btn = ctk.CTkButton(
                    widget_frame, 
                    text="×", 
                    width=20, 
                    height=20,
                    command=lambda wid=widget_id: self.remove_widget_from_group(wid)
                )
                remove_btn.pack(side="right", padx=2, pady=2)
        
        # Update widget count
        self.widget_count = len(self.group.widget_ids)
        self.count_label.configure(text=f"Widgets: {self.widget_count}")
    
    def add_widget_to_group(self):
        """Add a widget to the group"""
        # Get canvas reference
        canvas = self.master.canvas if hasattr(self.master, 'canvas') else None
        if not canvas:
            messagebox.showerror("Error", "Cannot access canvas")
            return
        
        # Get available widgets
        available_widgets = []
        for widget_id, widget in canvas.widgets.items():
            if widget_id not in self.group.widget_ids:
                available_widgets.append(widget)
        
        if not available_widgets:
            messagebox.showinfo("No Widgets", "No widgets available to add to this group.")
            return
        
        # Show widget selection dialog
        from ui import WidgetSelectionDialog
        WidgetSelectionDialog(
            self,
            available_widgets,
            self.on_widget_selected
        )
    
    def on_widget_selected(self, widget_id: str):
        """Handle widget selection from dialog"""
        # Get canvas reference
        canvas = self.master.canvas if hasattr(self.master, 'canvas') else None
        if not canvas:
            return
        
        # Add widget to group
        canvas.add_to_group(widget_id, self.group.id)
        self.update_widget_list()
        
        # Update group bounds and re-render
        canvas.update_group_bounds(self.group.id)
        canvas.render_group(self.group)
        
        messagebox.showinfo("Success", f"Widget added to group '{self.group.name}'")
    
    def remove_widget_from_group(self, widget_id: str):
        """Remove a widget from the group"""
        # Get canvas reference
        canvas = self.master.canvas if hasattr(self.master, 'canvas') else None
        if not canvas:
            return
        
        # Remove widget from group
        canvas.remove_from_group(widget_id, self.group.id)
        self.update_widget_list()
        
        # Update group bounds
        canvas.update_group_bounds(self.group.id)
        canvas.render_group(self.group)
    
    def remove_selected_widget(self):
        """Remove selected widget from group"""
        # For now, just show a message - in a full implementation, you'd have selection
        messagebox.showinfo("Remove Widget", "Click the '×' button next to a widget to remove it from the group.")
    
    def ok(self):
        """Apply changes and close dialog"""
        try:
            # Update group properties
            old_name = self.group.name
            self.group.name = self.name_entry.get().strip() or "Unnamed Group"
            self.group.layer = int(self.layer_var.get())
            self.group.visible = self.visible_var.get()
            self.group.locked = self.locked_var.get()
            
            # Get canvas reference to apply changes immediately
            canvas = self.master.canvas if hasattr(self.master, 'canvas') else None
            if canvas:
                # Update group bounds
                canvas.update_group_bounds(self.group.id)
                
                # Update layer for all widgets in group
                for widget_id in self.group.widget_ids:
                    if widget_id in canvas.widgets:
                        canvas.widgets[widget_id].layer = self.group.layer
                        canvas.render_widget(canvas.widgets[widget_id])
                
                # Force re-render of the group with updated name and properties
                canvas.delete(f"group_{self.group.id}")  # Remove old group rendering
                canvas.render_group(self.group)  # Re-render with new properties
                
                # Update layer list if visible
                if hasattr(self.master, 'layer_panel_frame') and self.master.layer_panel_frame.winfo_viewable():
                    self.master.update_layer_list()
            
            # Notify parent of changes
            self.on_group_update(self.group)
            
            # Show success message
            if old_name != self.group.name:
                messagebox.showinfo("Success", f"Group renamed to '{self.group.name}'")
            
            self.destroy()
            
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid layer number.")
    
    def cancel(self):
        """Cancel changes and close dialog"""
        self.destroy()
