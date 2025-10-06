#!/usr/bin/env python3
"""
Widget type definitions and data models for the GUI Builder application.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Any


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
    group_id: Optional[str] = None  # ID of the group this widget belongs to
    layer: int = 0  # Layer number (higher numbers are on top)
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type.value,
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'group_id': self.group_id,
            'layer': self.layer,
            'properties': {k: {'name': v.name, 'value': v.value, 'type': v.type, 'options': v.options} 
                          for k, v in self.properties.items()}
        }


@dataclass
class WidgetGroup:
    """Represents a group of widgets"""
    id: str
    name: str
    widget_ids: List[str]
    x: int
    y: int
    width: int
    height: int
    layer: int = 0
    visible: bool = True
    locked: bool = False
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'widget_ids': self.widget_ids,
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'layer': self.layer,
            'visible': self.visible,
            'locked': self.locked
        }
