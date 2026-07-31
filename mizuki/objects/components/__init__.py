from .actionrow import *
from .button import *
from .objectselect import *
from .staticui import *
from .stringselect import *
from .modal_child import *

type Component = (
    ActionRow
    | Button
    | StringSelect
    | TextInput
    | UserSelect
    | RoleSelect
    | MentionableSelect
    | ChannelSelect
    | Section
    | TextDisplay
    | Thumbnail
    | MediaGallery
    | FileComponent
    | Separator
    | Container
    | Label
    | RadioGroup
    | CheckboxGroup
    | Checkbox
)

type ComponentResponse = (
    ButtonResponse
    | StringSelectResponse
    | TextInputResponse
    | UserSelectResponse
    | RoleSelectResponse
    | MentionableSelectResponse
    | ChannelSelectResponse
    | RadioGroupResponse
    | CheckboxGroupResponse
    | CheckboxResponse
)
