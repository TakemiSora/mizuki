from .actionrow import *
from .button import *
from .objectselect import *
from .staticui import *
from .stringselect import *
from .textinput import *

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
)

type ComponentResponse = (
    ButtonResponse
    | StringSelectResponse
    | UserSelectResponse
    | RoleSelectResponse
    | MentionableSelectResponse
    | ChannelSelectResponse
)
