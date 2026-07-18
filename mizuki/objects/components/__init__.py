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
    | TextDisplay
)
