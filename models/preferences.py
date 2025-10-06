#!/usr/bin/env python3
"""
Application preferences and configuration management.
"""

import json
import os
from dataclasses import dataclass, asdict
from typing import Any


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
