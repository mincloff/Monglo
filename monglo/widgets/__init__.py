"""
Widget exports.

All widget classes are available for import from monglo.widgets.
"""

from .base import BaseWidget
from .inputs import (
    TextInput,
    TextArea,
    NumberInput,
    EmailInput,
    PasswordInput,
    DatePicker,
    DateTimePicker,
    CheckboxInput,
    ColorPicker
)
from .selects import (
    Select,
    MultiSelect,
    Autocomplete,
    RadioButtons,
    ReferenceSelect
)
from .displays import (
    Label,
    Badge,
    Link,
    Image,
    JSONDisplay,
    CodeDisplay,
    ProgressBar
)
from .custom import (
    CustomWidget,
    WidgetGroup,
    ConditionalWidget
)

__all__ = [
    # Base
    "BaseWidget",
    # Inputs
    "TextInput",
    "TextArea",
    "NumberInput",
    "EmailInput",
    "PasswordInput",
    "DatePicker",
    "DateTimePicker",
    "CheckboxInput",
    "ColorPicker",
    # Selects
    "Select",
    "MultiSelect",
    "Autocomplete",
    "RadioButtons",
    "ReferenceSelect",
    # Displays
    "Label",
    "Badge",
    "Link",
    "Image",
    "JSONDisplay",
    "CodeDisplay",
    "ProgressBar",
    # Custom
    "CustomWidget",
    "WidgetGroup",
    "ConditionalWidget",
]
