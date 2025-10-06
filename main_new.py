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
import sys
from typing import Dict, List, Optional, Any

# Import from our new modular structure
from models import WidgetType, WidgetProperty, WidgetData, AppPreferences, PreferencesManager
from ui import WidgetToolbox, DesignCanvas, PropertiesEditor, CodeEditor, PopOutCodeEditor
from core import CodeParser, CodeGenerator
from utils import APP_NAME, APP_VERSION

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class GUIBuilderApp(ctk.CTk):
    """Main application class - Professional Python GUI Builder MVP"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize preferences manager
        self.prefs_manager = PreferencesManager()
        
        # Apply appearance preferences
        self.apply_appearance_preferences()
        
        self.title(f"{APP_NAME} - MVP v{APP_VERSION}")
        
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
    
    def setup_status_bar(self):
        """Setup the status bar"""
        self.status_bar = ctk.CTkLabel(
            self, 
            text="Ready", 
            font=ctk.CTkFont(size=12),
            anchor="w"
        )
        self.status_bar.grid(row=2, column=0, columnspan=3, sticky="ew", padx=5, pady=2)
    
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
            self.code_controls_frame,
            text="🔄 Sync from Code",
            command=self.sync_from_code,
            width=120
        )
        self.code_sync_button.pack(side="left", padx=5)
        
        self.code_export_button = ctk.CTkButton(
            self.code_controls_frame,
            text="💾 Export Code",
            command=self.export_code,
            width=120
        )
        self.code_export_button.pack(side="left", padx=5)
    
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
    
    def setup_toolbar(self):
        """Setup the toolbar"""
        self.toolbar = ctk.CTkFrame(self)
        self.toolbar.grid(row=0, column=0, columnspan=3, sticky="ew", padx=5, pady=2)
        
        # Toolbar buttons
        self.new_button = ctk.CTkButton(self.toolbar, text="📄 New", command=self.new_project, width=80)
        self.new_button.pack(side="left", padx=2)
        
        self.open_button = ctk.CTkButton(self.toolbar, text="📂 Open", command=self.open_project, width=80)
        self.open_button.pack(side="left", padx=2)
        
        self.save_button = ctk.CTkButton(self.toolbar, text="💾 Save", command=self.save_project, width=80)
        self.save_button.pack(side="left", padx=2)
        
        # Separator
        separator = ctk.CTkFrame(self.toolbar, width=2, height=30)
        separator.pack(side="left", padx=5)
        
        self.preview_button = ctk.CTkButton(self.toolbar, text="👁️ Preview", command=self.preview_gui, width=80)
        self.preview_button.pack(side="left", padx=2)
        
        self.export_button = ctk.CTkButton(self.toolbar, text="📤 Export", command=self.export_python, width=80)
        self.export_button.pack(side="left", padx=2)
        
        # Separator
        separator2 = ctk.CTkFrame(self.toolbar, width=2, height=30)
        separator2.pack(side="left", padx=5)
        
        self.code_view_button = ctk.CTkButton(self.toolbar, text="📝 Code View", command=self.toggle_code_view, width=100)
        self.code_view_button.pack(side="left", padx=2)
        
        self.grid_button = ctk.CTkButton(self.toolbar, text="🔲 Grid", command=self.toggle_grid, width=80)
        self.grid_button.pack(side="left", padx=2)
    
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
    
    def apply_appearance_preferences(self):
        """Apply appearance preferences from settings"""
        appearance_mode = self.prefs_manager.get("appearance_mode", "dark")
        color_theme = self.prefs_manager.get("color_theme", "blue")
        
        ctk.set_appearance_mode(appearance_mode)
        ctk.set_default_color_theme(color_theme)
    
    def apply_window_preferences(self):
        """Apply window preferences from settings"""
        width = self.prefs_manager.get("window_width", 1400)
        height = self.prefs_manager.get("window_height", 900)
        x = self.prefs_manager.get("window_x", 100)
        y = self.prefs_manager.get("window_y", 100)
        
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def on_widget_drag_start(self, widget_type: WidgetType):
        """Handle widget drag start from toolbox"""
        # This is handled by the toolbox itself
        pass
    
    def on_widget_select(self, widget_data: Optional[WidgetData]):
        """Handle widget selection"""
        self.properties_editor.set_widget(widget_data)
        if widget_data:
            self.status_bar.configure(text=f"Selected: {widget_data.type.value}")
        else:
            self.status_bar.configure(text="No widget selected")
    
    def on_property_change(self, property_name: str, value: Any):
        """Handle property changes"""
        if hasattr(self.canvas, 'selected_widget_id') and self.canvas.selected_widget_id:
            self.canvas.update_widget_property(self.canvas.selected_widget_id, property_name, value)
            self.status_bar.configure(text=f"Updated {property_name}")
    
    def on_code_change(self, code: str):
        """Handle code editor changes"""
        # Update the code editor content
        pass
    
    def toggle_code_view(self):
        """Toggle code editor visibility"""
        if self.code_editor_frame.winfo_viewable():
            self.code_editor_frame.grid_remove()
            self.code_view_button.configure(text="📝 Code View")
        else:
            self.code_editor_frame.grid()
            self.code_view_button.configure(text="📝 Hide Code")
            self.generate_code()
    
    def toggle_grid(self):
        """Toggle grid visibility"""
        if hasattr(self.canvas, 'show_grid'):
            self.canvas.show_grid = not self.canvas.show_grid
            self.canvas.draw_grid()
            self.status_bar.configure(text=f"Grid {'enabled' if self.canvas.show_grid else 'disabled'}")
    
    def generate_code(self):
        """Generate Python code from current widgets"""
        if hasattr(self.canvas, 'widgets'):
            code = CodeGenerator.generate_code(self.canvas.widgets, self.window_properties)
            if hasattr(self, 'code_editor'):
                self.code_editor.set_code(code)
    
    def sync_from_code(self):
        """Sync widgets from code editor"""
        if hasattr(self, 'code_editor'):
            code = self.code_editor.get_code()
            widgets, window_props = CodeParser.parse_code_to_widgets(code)
            
            # Update canvas with parsed widgets
            self.canvas.widgets = widgets
            self.window_properties.update(window_props)
            
            # Re-render canvas
            self.canvas.delete("all")
            for widget in widgets.values():
                self.canvas.render_widget(widget)
            self.canvas.draw_grid()
            
            self.status_bar.configure(text="Synced from code")
    
    def export_code(self):
        """Export code from editor"""
        if hasattr(self, 'code_editor'):
            code = self.code_editor.get_code()
            file_path = filedialog.asksaveasfilename(
                title="Export Python Code",
                defaultextension=".py",
                filetypes=[("Python files", "*.py"), ("All files", "*.*")]
            )
            
            if file_path:
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(code)
                    self.status_bar.configure(text=f"Code exported: {os.path.basename(file_path)}")
                except Exception as e:
                    messagebox.showerror("Export Error", f"Failed to export code: {str(e)}")
    
    def new_project(self):
        """Create a new project"""
        if self.project_modified:
            if not messagebox.askyesno("Unsaved Changes", "You have unsaved changes. Create new project anyway?"):
                return
        
        # Clear canvas
        self.canvas.widgets.clear()
        self.canvas.delete("all")
        self.canvas.draw_grid()
        self.canvas.deselect_all()
        
        # Reset state
        self.current_file = None
        self.project_modified = False
        self.status_bar.configure(text="New project created")
    
    def open_project(self):
        """Open an existing project"""
        file_path = filedialog.askopenfilename(
            title="Open Project",
            filetypes=[("GUI Builder files", "*.pygui"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Load widgets
                self.canvas.widgets.clear()
                self.canvas.delete("all")
                
                for widget_data in data.get('widgets', []):
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
                    self.canvas.widgets[widget.id] = widget
                    self.canvas.render_widget(widget)
                
                # Load window properties
                self.window_properties.update(data.get('window_properties', {}))
                
                self.canvas.draw_grid()
                self.current_file = file_path
                self.project_modified = False
                self.status_bar.configure(text=f"Opened: {os.path.basename(file_path)}")
                
            except Exception as e:
                messagebox.showerror("Open Error", f"Failed to open project: {str(e)}")
    
    def save_project(self):
        """Save the current project"""
        if self.current_file:
            file_path = self.current_file
        else:
            file_path = filedialog.asksaveasfilename(
                title="Save Project",
                defaultextension=".pygui",
                filetypes=[("GUI Builder files", "*.pygui"), ("All files", "*.*")]
            )
        
        if file_path:
            try:
                data = {
                    'widgets': [widget.to_dict() for widget in self.canvas.widgets.values()],
                    'window_properties': self.window_properties
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                
                self.current_file = file_path
                self.project_modified = False
                self.status_bar.configure(text=f"Saved: {os.path.basename(file_path)}")
                
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save project: {str(e)}")
    
    def export_python(self):
        """Export as Python file"""
        if not self.canvas.widgets:
            messagebox.showwarning("No Widgets", "Please add some widgets before exporting.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export Python Code",
            defaultextension=".py",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                code = CodeGenerator.generate_code(self.canvas.widgets, self.window_properties)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(code)
                
                self.status_bar.configure(text=f"Exported: {os.path.basename(file_path)}")
                messagebox.showinfo("Export Successful", f"Python code exported to:\n{file_path}")
                
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export Python code: {str(e)}")
    
    def preview_gui(self):
        """Preview the generated GUI"""
        if not self.canvas.widgets:
            messagebox.showwarning("No Widgets", "Please add some widgets before previewing.")
            return
        
        try:
            code = CodeGenerator.generate_code(self.canvas.widgets, self.window_properties)
            
            # Create a temporary file for preview
            temp_file = "temp_preview.py"
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # Execute the preview
            import subprocess
            subprocess.Popen([sys.executable, temp_file])
            
            self.status_bar.configure(text="Preview opened")
            
        except Exception as e:
            messagebox.showerror("Preview Error", f"Failed to create preview: {str(e)}")
    
    def clear_canvas(self):
        """Clear all widgets from canvas"""
        if self.canvas.widgets and messagebox.askyesno("Clear Canvas", "Are you sure you want to clear all widgets?"):
            self.canvas.widgets.clear()
            self.canvas.delete("all")
            self.canvas.draw_grid()
            self.canvas.deselect_all()
            self.project_modified = True
            self.status_bar.configure(text="Canvas cleared")
    
    def show_preferences(self):
        """Show preferences window"""
        from ui import PreferencesWindow
        PreferencesWindow(self, self.prefs_manager)
    
    def load_recent_files(self):
        """Load recent files list"""
        try:
            if os.path.exists("recent_files.json"):
                with open("recent_files.json", 'r', encoding='utf-8') as f:
                    self.recent_files = json.load(f)
        except:
            self.recent_files = []
    
    def save_recent_files(self):
        """Save recent files list"""
        try:
            with open("recent_files.json", 'w', encoding='utf-8') as f:
                json.dump(self.recent_files, f, indent=2)
        except:
            pass
    
    def update_status_info(self):
        """Update status bar with project info"""
        widget_count = len(self.canvas.widgets) if hasattr(self.canvas, 'widgets') else 0
        status = f"Widgets: {widget_count}"
        if self.project_modified:
            status += " (Modified)"
        self.status_bar.configure(text=status)
    
    def on_main_window_close(self):
        """Handle main window close"""
        if self.project_modified:
            if messagebox.askyesno("Unsaved Changes", "You have unsaved changes. Exit anyway?"):
                self.destroy()
        else:
            self.destroy()
    
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
        """Load project from file path"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Clear current canvas
            self.canvas.widgets.clear()
            self.canvas.delete("all")
            self.canvas.draw_grid()
            
            # Load widgets
            for widget_data in data.get('widgets', []):
                widget_type = WidgetType(widget_data['type'])
                widget = WidgetData(
                    id=widget_data['id'],
                    type=widget_type,
                    x=widget_data['x'],
                    y=widget_data['y'],
                    width=widget_data['width'],
                    height=widget_data['height'],
                    properties={}
                )
                self.canvas.widgets[widget.id] = widget
            
            # Load window properties
            self.window_properties = data.get('window_properties', {})
            
            # Update UI
            self.canvas.render_all_widgets()
            self.current_file = file_path
            self.project_modified = False
            self.update_status_info()
            self.status_bar.configure(text=f"Project loaded: {os.path.basename(file_path)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load project: {str(e)}")
    
    def add_to_recent_files(self, file_path: str):
        """Add file to recent files list"""
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        # Keep only the most recent 10 files
        self.recent_files = self.recent_files[:10]
        self.save_recent_files()
        self.update_recent_menu()
    
    def toggle_grid_snap(self):
        """Toggle grid snap"""
        self.canvas.snap_to_grid = not self.canvas.snap_to_grid
        self.status_bar.configure(text=f"Grid snap: {'ON' if self.canvas.snap_to_grid else 'OFF'}")
    
    def toggle_window_boundary(self):
        """Toggle window boundary display"""
        self.canvas.window_boundary_visible = not self.canvas.window_boundary_visible
        self.canvas.draw_window_boundary()
        self.status_bar.configure(text=f"Window boundary: {'ON' if self.canvas.window_boundary_visible else 'OFF'}")
    
    def set_theme(self, theme: str):
        """Set appearance theme"""
        ctk.set_appearance_mode(theme)
        self.prefs_manager.set("appearance_mode", theme)
        self.status_bar.configure(text=f"Theme set to: {theme}")
    
    def set_color_theme(self, color_theme: str):
        """Set color theme"""
        ctk.set_default_color_theme(color_theme)
        self.prefs_manager.set("color_theme", color_theme)
        self.status_bar.configure(text=f"Color theme set to: {color_theme}")
    
    def show_window_properties(self):
        """Show window properties dialog"""
        from ui import WindowPropertiesDialog
        WindowPropertiesDialog(self, self.window_properties, self.apply_window_properties)
    
    def apply_window_properties(self, properties: Dict[str, Any]):
        """Apply window properties changes"""
        self.window_properties.update(properties)
        self.project_modified = True
        self.update_status_info()
        self.status_bar.configure(text="Window properties updated")
    
    def show_shortcuts(self):
        """Show keyboard shortcuts dialog"""
        shortcuts = """
Keyboard Shortcuts:

File Operations:
Ctrl+N - New Project
Ctrl+O - Open Project
Ctrl+S - Save Project
Ctrl+Shift+S - Save As
Ctrl+E - Export Python

Edit Operations:
Ctrl+Z - Undo
Ctrl+Y - Redo
Ctrl+X - Cut
Ctrl+C - Copy
Ctrl+V - Paste
Ctrl+D - Duplicate
Ctrl+A - Select All
Del - Delete

View Operations:
Ctrl+G - Toggle Grid
Ctrl+Shift+G - Toggle Grid Snap
Ctrl+B - Toggle Window Boundary
Ctrl+Shift+V - Toggle Code View

Tools:
F5 - Preview GUI
Ctrl+, - Preferences
        """
        messagebox.showinfo("Keyboard Shortcuts", shortcuts)
    
    def show_about(self):
        """Show about dialog"""
        about_text = f"""
{APP_NAME} {APP_VERSION}

A professional Python GUI builder using CustomTkinter.

Features:
• Visual drag-and-drop interface
• Real-time code generation
• Multiple widget types
• Grid-based design
• Undo/Redo support
• Export to Python code

Built with Python and CustomTkinter.
        """
        messagebox.showinfo("About", about_text)
    
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
            
        except Exception as e:
            print(f"Error handling pop-out window close: {e}")
            self.status_bar.configure(text=f"Error: {str(e)}")
    
    def sync_code_from_design(self):
        """Sync code editor with current design"""
        if not self.canvas.widgets:
            if hasattr(self, 'code_editor'):
                self.code_editor.set_code("# No widgets in design yet.\n# Add some widgets to see the generated code here.")
            return
        
        try:
            code = CodeGenerator.generate_code(self.canvas.widgets, self.window_properties)
            if hasattr(self, 'code_editor'):
                self.code_editor.set_code(code)
            self.status_bar.configure(text="Code synced from design")
        except Exception as e:
            error_code = f"# Error generating code: {str(e)}\n# Please check your design and try again."
            if hasattr(self, 'code_editor'):
                self.code_editor.set_code(error_code)
            self.status_bar.configure(text="Error syncing code")
    
    def validate_code(self):
        """Validate the current code in the editor"""
        if not hasattr(self, 'code_editor'):
            return
            
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
        if not hasattr(self, 'code_editor'):
            return
            
        code = self.code_editor.get_code()
        
        try:
            # Create a temporary file for running
            temp_file = "temp_run.py"
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # Execute the code
            import subprocess
            subprocess.Popen([sys.executable, temp_file])
            
            self.status_bar.configure(text="Code executed")
            
        except Exception as e:
            messagebox.showerror("Execution Error", f"Failed to run code: {str(e)}")
    
    def export_edited_code(self):
        """Export the current code from the editor"""
        if not hasattr(self, 'code_editor'):
            return
            
        code = self.code_editor.get_code()
        file_path = filedialog.asksaveasfilename(
            title="Export Python Code",
            defaultextension=".py",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(code)
                self.status_bar.configure(text=f"Code exported: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export code: {str(e)}")
    
    def on_global_delete(self, event):
        """Global delete key handler"""
        # Check if focus is on a text input widget in properties editor
        if hasattr(self, 'properties_editor'):
            focused_widget = self.focus_get()
            if focused_widget and self.is_properties_text_widget(focused_widget):
                # Don't delete widget if typing in properties editor
                return
        
        # Forward to canvas delete handler
        if hasattr(self, 'canvas'):
            self.canvas.on_delete_key(event)
    
    def is_properties_text_widget(self, widget):
        """Check if widget is a text input in properties editor"""
        try:
            # Check if widget is in properties editor
            parent = widget.master
            while parent:
                if hasattr(parent, 'winfo_name') and 'properties' in str(parent.winfo_name()).lower():
                    return True
                parent = parent.master
            return False
        except:
            return False
    
    def on_global_copy(self, event):
        """Global copy handler"""
        if hasattr(self, 'canvas'):
            self.canvas.on_copy(event)
    
    def on_global_paste(self, event):
        """Global paste handler"""
        if hasattr(self, 'canvas'):
            self.canvas.on_paste(event)
    
    def on_global_cut(self, event):
        """Global cut handler"""
        if hasattr(self, 'canvas'):
            self.canvas.on_cut(event)
    
    def on_global_undo(self, event):
        """Global undo handler"""
        if hasattr(self, 'canvas'):
            self.canvas.on_undo(event)
    
    def on_global_redo(self, event):
        """Global redo handler"""
        if hasattr(self, 'canvas'):
            self.canvas.on_redo(event)
    
    def on_global_save(self, event):
        """Global save handler"""
        self.save_project()
    
    def on_global_new(self, event):
        """Global new project handler"""
        self.new_project()
    
    def on_global_open(self, event):
        """Global open project handler"""
        self.open_project()
    
    def on_global_preview(self, event):
        """Global preview handler"""
        self.preview_gui()
    
    def on_global_escape(self, event):
        """Global escape handler"""
        if hasattr(self, 'canvas'):
            self.canvas.deselect_all()
    
    def on_global_toggle_grid(self, event):
        """Global toggle grid handler"""
        self.toggle_grid()
    
    def on_global_toggle_grid_snap(self, event):
        """Global toggle grid snap handler"""
        self.toggle_grid_snap()
    
    def on_global_export(self, event):
        """Global export handler"""
        self.export_python()
    
    def on_global_toggle_code_view(self, event):
        """Global toggle code view handler"""
        self.toggle_code_view()
    
    def on_global_toggle_window_boundary(self, event):
        """Global toggle window boundary handler"""
        self.toggle_window_boundary()
    
    def on_global_preferences(self, event):
        """Global preferences handler"""
        self.show_preferences()


def main():
    """Main entry point"""
    app = GUIBuilderApp()
    app.mainloop()


if __name__ == "__main__":
    main()
