#!/usr/bin/env python3
"""
Preferences window for the GUI Builder application.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, colorchooser
from dataclasses import asdict
from typing import Optional

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
            from .preferences_window import PreferencesWindow
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
