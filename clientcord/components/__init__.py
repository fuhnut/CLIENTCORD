from __future__ import annotations
from typing import Any
import msgspec


IS_COMPONENTS_V2 = 1 << 15


class ComponentType:
    action_row = 1
    button = 2
    string_select = 3
    text_input = 4
    user_select = 5
    role_select = 6
    mentionable_select = 7
    channel_select = 8
    section = 9
    text_display = 10
    thumbnail = 11
    media_gallery = 12
    file = 13
    separator = 14
    container = 17


class ButtonStyle:
    primary = 1
    secondary = 2
    success = 3
    danger = 4
    link = 5
    premium = 6


class TextInputStyle:
    short = 1
    paragraph = 2


class Button:
    def __init__(self) -> None:
        self._data: dict[str, Any] = {"type": ComponentType.button}

    def set_custom_id(self, custom_id: str) -> Button:
        self._data["custom_id"] = custom_id
        return self

    def set_label(self, label: str) -> Button:
        self._data["label"] = label
        return self

    def set_style(self, style: int) -> Button:
        self._data["style"] = style
        return self

    def set_url(self, url: str) -> Button:
        self._data["url"] = url
        return self

    def set_disabled(self, disabled: bool = True) -> Button:
        self._data["disabled"] = disabled
        return self

    def to_dict(self) -> dict[str, Any]:
        return self._data


class StringSelectOption:
    def __init__(self) -> None:
        self._data: dict[str, Any] = {}

    def set_label(self, label: str) -> StringSelectOption:
        self._data["label"] = label
        return self

    def set_value(self, value: str) -> StringSelectOption:
        self._data["value"] = value
        return self

    def set_description(self, description: str) -> StringSelectOption:
        self._data["description"] = description
        return self

    def to_dict(self) -> dict[str, Any]:
        return self._data


class StringSelectMenu:
    def __init__(self) -> None:
        self._data: dict[str, Any] = {"type": ComponentType.string_select}

    def set_custom_id(self, custom_id: str) -> StringSelectMenu:
        self._data["custom_id"] = custom_id
        return self

    def set_placeholder(self, placeholder: str) -> StringSelectMenu:
        self._data["placeholder"] = placeholder
        return self

    def set_options(self, options: list[StringSelectOption]) -> StringSelectMenu:
        self._data["options"] = [o.to_dict() for o in options]
        return self

    def set_min_values(self, min_values: int) -> StringSelectMenu:
        self._data["min_values"] = min_values
        return self

    def set_max_values(self, max_values: int) -> StringSelectMenu:
        self._data["max_values"] = max_values
        return self

    def set_disabled(self, disabled: bool = True) -> StringSelectMenu:
        self._data["disabled"] = disabled
        return self

    def to_dict(self) -> dict[str, Any]:
        return self._data


class UserSelectMenu:
    def __init__(self) -> None:
        self._data: dict[str, Any] = {"type": ComponentType.user_select}

    def set_custom_id(self, custom_id: str) -> UserSelectMenu:
        self._data["custom_id"] = custom_id
        return self

    def set_placeholder(self, placeholder: str) -> UserSelectMenu:
        self._data["placeholder"] = placeholder
        return self

    def set_min_values(self, min_values: int) -> UserSelectMenu:
        self._data["min_values"] = min_values
        return self

    def set_max_values(self, max_values: int) -> UserSelectMenu:
        self._data["max_values"] = max_values
        return self

    def to_dict(self) -> dict[str, Any]:
        return self._data


class RoleSelectMenu:
    def __init__(self) -> None:
        self._data: dict[str, Any] = {"type": ComponentType.role_select}

    def set_custom_id(self, custom_id: str) -> RoleSelectMenu:
        self._data["custom_id"] = custom_id
        return self

    def set_placeholder(self, placeholder: str) -> RoleSelectMenu:
        self._data["placeholder"] = placeholder
        return self

    def set_min_values(self, min_values: int) -> RoleSelectMenu:
        self._data["min_values"] = min_values
        return self

    def set_max_values(self, max_values: int) -> RoleSelectMenu:
        self._data["max_values"] = max_values
        return self

    def to_dict(self) -> dict[str, Any]:
        return self._data


class ChannelSelectMenu:
    def __init__(self) -> None:
        self._data: dict[str, Any] = {"type": ComponentType.channel_select}

    def set_custom_id(self, custom_id: str) -> ChannelSelectMenu:
        self._data["custom_id"] = custom_id
        return self

    def set_placeholder(self, placeholder: str) -> ChannelSelectMenu:
        self._data["placeholder"] = placeholder
        return self

    def set_channel_types(self, channel_types: list[int]) -> ChannelSelectMenu:
        self._data["channel_types"] = channel_types
        return self

    def set_min_values(self, min_values: int) -> ChannelSelectMenu:
        self._data["min_values"] = min_values
        return self

    def set_max_values(self, max_values: int) -> ChannelSelectMenu:
        self._data["max_values"] = max_values
        return self

    def to_dict(self) -> dict[str, Any]:
        return self._data


class MentionableSelectMenu:
    def __init__(self) -> None:
        self._data: dict[str, Any] = {"type": ComponentType.mentionable_select}

    def set_custom_id(self, custom_id: str) -> MentionableSelectMenu:
        self._data["custom_id"] = custom_id
        return self

    def set_placeholder(self, placeholder: str) -> MentionableSelectMenu:
        self._data["placeholder"] = placeholder
        return self

    def set_min_values(self, min_values: int) -> MentionableSelectMenu:
        self._data["min_values"] = min_values
        return self

    def set_max_values(self, max_values: int) -> MentionableSelectMenu:
        self._data["max_values"] = max_values
        return self

    def to_dict(self) -> dict[str, Any]:
        return self._data


class TextInput:
    def __init__(self) -> None:
        self._data: dict[str, Any] = {"type": ComponentType.text_input}

    def set_custom_id(self, custom_id: str) -> TextInput:
        self._data["custom_id"] = custom_id
        return self

    def set_style(self, style: int) -> TextInput:
        self._data["style"] = style
        return self

    def set_placeholder(self, placeholder: str) -> TextInput:
        self._data["placeholder"] = placeholder
        return self

    def set_value(self, value: str) -> TextInput:
        self._data["value"] = value
        return self

    def set_required(self, required: bool = True) -> TextInput:
        self._data["required"] = required
        return self

    def set_length(self, *, min: int | None = None, max: int | None = None) -> TextInput:
        if min is not None:
            self._data["min_length"] = min
        if max is not None:
            self._data["max_length"] = max
        return self

    def to_dict(self) -> dict[str, Any]:
        return self._data


class TextDisplay:
    def __init__(self) -> None:
        self._data: dict[str, Any] = {"type": ComponentType.text_display}

    def set_content(self, content: str) -> TextDisplay:
        self._data["content"] = content
        return self

    def set_id(self, id: int) -> TextDisplay:
        self._data["id"] = id
        return self

    def to_dict(self) -> dict[str, Any]:
        return self._data


class Thumbnail:
    def __init__(self) -> None:
        self._data: dict[str, Any] = {"type": ComponentType.thumbnail}

    def set_url(self, url: str) -> Thumbnail:
        self._data["media"] = {"url": url}
        return self

    def to_dict(self) -> dict[str, Any]:
        return self._data


class MediaGalleryItem:
    def __init__(self) -> None:
        self._data: dict[str, Any] = {}

    def set_url(self, url: str) -> MediaGalleryItem:
        self._data["media"] = {"url": url}
        return self

    def set_description(self, description: str) -> MediaGalleryItem:
        self._data["description"] = description
        return self

    def set_spoiler(self, spoiler: bool = True) -> MediaGalleryItem:
        self._data["spoiler"] = spoiler
        return self

    def to_dict(self) -> dict[str, Any]:
        return self._data


class MediaGallery:
    def __init__(self) -> None:
        self._data: dict[str, Any] = {"type": ComponentType.media_gallery}

    def set_items(self, items: list[MediaGalleryItem]) -> MediaGallery:
        self._data["items"] = [i.to_dict() for i in items]
        return self

    def to_dict(self) -> dict[str, Any]:
        return self._data


class FileComponent:
    def __init__(self) -> None:
        self._data: dict[str, Any] = {"type": ComponentType.file}

    def set_url(self, url: str) -> FileComponent:
        self._data["file"] = {"url": url}
        return self

    def to_dict(self) -> dict[str, Any]:
        return self._data


class Separator:
    def __init__(self) -> None:
        self._data: dict[str, Any] = {"type": ComponentType.separator, "divider": True, "spacing": 1}

    def set_divider(self, divider: bool) -> Separator:
        self._data["divider"] = divider
        return self

    def set_spacing(self, spacing: int) -> Separator:
        self._data["spacing"] = spacing
        return self

    def to_dict(self) -> dict[str, Any]:
        return self._data


class ActionRow:
    def __init__(self) -> None:
        self._data: dict[str, Any] = {"type": ComponentType.action_row, "components": []}

    def set_components(self, components: list[Any]) -> ActionRow:
        self._data["components"] = [c.to_dict() for c in components]
        return self

    def add_components(self, *components: Any) -> ActionRow:
        for c in components:
            self._data["components"].append(c.to_dict())
        return self

    def to_dict(self) -> dict[str, Any]:
        return self._data


class Section:
    def __init__(self) -> None:
        self._data: dict[str, Any] = {"type": ComponentType.section, "components": []}

    def set_components(self, components: list[Any]) -> Section:
        self._data["components"] = [c.to_dict() for c in components]
        return self

    def set_accessory(self, accessory: Any) -> Section:
        self._data["accessory"] = accessory.to_dict()
        return self

    def to_dict(self) -> dict[str, Any]:
        return self._data


class Container:
    def __init__(self) -> None:
        self._data: dict[str, Any] = {"type": ComponentType.container, "components": []}

    def set_components(self, components: list[Any]) -> Container:
        self._data["components"] = [c.to_dict() for c in components]
        return self

    def set_accent_color(self, color: int) -> Container:
        self._data["accent_color"] = color
        return self

    def set_spoiler(self, spoiler: bool = True) -> Container:
        self._data["spoiler"] = spoiler
        return self

    def to_dict(self) -> dict[str, Any]:
        return self._data


class Label:
    def __init__(self) -> None:
        self._data: dict[str, Any] = {"type": 18}

    def set_label(self, label: str) -> Label:
        self._data["label"] = label
        return self

    def set_description(self, description: str) -> Label:
        self._data["description"] = description
        return self

    def set_component(self, component: Any) -> Label:
        self._data["component"] = component.to_dict()
        return self

    def to_dict(self) -> dict[str, Any]:
        return self._data


class Modal:
    def __init__(self) -> None:
        self._data: dict[str, Any] = {"components": []}

    def set_title(self, title: str) -> Modal:
        self._data["title"] = title
        return self

    def set_custom_id(self, custom_id: str) -> Modal:
        self._data["custom_id"] = custom_id
        return self

    def set_components(self, components: list[Any]) -> Modal:
        self._data["components"] = [c.to_dict() for c in components]
        return self

    def to_dict(self) -> dict[str, Any]:
        return self._data


class ComponentCommand:
    component_type: str = "Button"

    def filter(self, ctx: Any) -> bool:
        return True

    async def run(self, ctx: Any) -> None:
        pass


class ModalCommand:
    def filter(self, ctx: Any) -> bool:
        return True

    async def run(self, ctx: Any) -> None:
        pass


def build_components_payload(components: list[Any]) -> dict[str, Any]:
    return {
        "flags": IS_COMPONENTS_V2,
        "components": [c.to_dict() for c in components],
    }
