"""Swipeable component."""

from typing import Literal, TypedDict

import reflex as rx
from reflex.components.component import StatefulComponent
from reflex.constants.compiler import Hooks, Imports
from reflex.event import EventType, no_args_event_spec
from reflex.utils.format import to_camel_case
from reflex.utils.imports import ImportDict, ImportVar
from reflex.vars import FunctionStringVar, Var, get_unique_variable_name
from reflex.vars.base import VarData


class SwipeEvent(TypedDict):
    """A swipe event."""

    # direction of swipe
    dir: Literal["Left", "Right", "Up", "Down"]

    # initial swipe [x,y]
    initial: tuple[float, float]

    # true for the first event of a tracked swipe
    first: bool

    # x offset (current.x - initial.x)
    delta_x: float

    # y offset (current.y - initial.y)
    delta_y: float

    # absolute delta_x
    abs_x: float

    # absolute delta_y
    abs_y: float

    # √(absX^2 + absY^2) / time - "absolute velocity" (speed)
    velocity: float

    # [ deltaX/time, deltaY/time] - velocity per axis
    vxvy: tuple[float, float]


def swipe_event_data_spec(ev: Var[dict]) -> tuple[Var[SwipeEvent]]:
    """Create a swipe event data spec."""
    ev = ev.to(dict)
    return (
        Var.create(  # pyright: ignore[reportReturnType]
            {
                "dir": ev.dir,
                "initial": ev.initial,
                "first": ev.first,
                "delta_x": ev.deltaX,
                "delta_y": ev.deltaY,
                "abs_x": ev.absX,
                "abs_y": ev.absY,
                "velocity": ev.velocity,
                "vxvy": ev.vxvy,
            }
        ),
    )


class GhostSwipeable(rx.Fragment):
    """A ghost swipeable component."""

    on_swiped: rx.EventHandler[swipe_event_data_spec]
    on_swiped_left: rx.EventHandler[swipe_event_data_spec]
    on_swiped_right: rx.EventHandler[swipe_event_data_spec]
    on_swiped_up: rx.EventHandler[swipe_event_data_spec]
    on_swiped_down: rx.EventHandler[swipe_event_data_spec]
    on_swiped_start: rx.EventHandler[swipe_event_data_spec]
    on_swiping: rx.EventHandler[swipe_event_data_spec]

    on_tap = rx.EventHandler[no_args_event_spec]
    on_touch_start_or_mouse_down = rx.EventHandler[no_args_event_spec]
    on_touch_end_or_mouse_up = rx.EventHandler[no_args_event_spec]


class Swipeable(rx.Component):
    """A swipeable component."""

    library = "react-swipeable"

    # After any swipe
    on_swiped: rx.EventHandler[swipe_event_data_spec]

    # After a left swipe
    on_swiped_left: rx.EventHandler[swipe_event_data_spec]

    # After a right swipe
    on_swiped_right: rx.EventHandler[swipe_event_data_spec]

    # After an up swipe
    on_swiped_up: rx.EventHandler[swipe_event_data_spec]

    # After a down swipe
    on_swiped_down: rx.EventHandler[swipe_event_data_spec]

    # After a swipe has started
    on_swiped_start: rx.EventHandler[swipe_event_data_spec]

    # While swiping
    on_swiping: rx.EventHandler[swipe_event_data_spec]

    # After a tap
    on_tap = rx.EventHandler[no_args_event_spec]

    # After a touch start or mouse down
    on_touch_start_or_mouse_down = rx.EventHandler[no_args_event_spec]

    # After a touch end or mouse up
    on_touch_end_or_mouse_up = rx.EventHandler[no_args_event_spec]

    # min distance(px) before a swipe starts.
    delta: Var[float]

    # prevents scroll during swipe
    prevent_scroll_on_swipe: Var[bool]

    # track touch input
    track_touch: Var[bool]

    # track mouse input
    track_mouse: Var[bool]

    # set a rotation angle
    rotation_angle: Var[float]

    # allowable duration of a swipe (ms).
    swipe_duration: Var[float]

    def add_imports(self) -> ImportDict:
        """Add imports for the component."""
        return {
            "react-swipeable": ImportVar("useSwipeable"),
        }

    @classmethod
    def create(cls, *children, **props) -> rx.Component:
        """Create a swipeable component.

        Args:
            *children: The children of the component.
            **props: The properties of the component.

        Returns:
            The swipeable component.
        """
        unique_name = get_unique_variable_name()

        config_props_names = [
            "delta",
            "prevent_scroll_on_swipe",
            "track_touch",
            "track_mouse",
            "rotation_angle",
            "swipe_duration",
        ]

        config_mapping = {k: props.pop(k, None) for k in config_props_names}

        event_names = [
            "on_swiped",
            "on_swiped_left",
            "on_swiped_right",
            "on_swiped_up",
            "on_swiped_down",
            "on_swiped_start",
            "on_swiping",
            "on_tap",
            "on_touch_start_or_mouse_down",
            "on_touch_end_or_mouse_up",
        ]

        event_mapping = {k: props.pop(k, None) for k in event_names}

        event_triggers = StatefulComponent._get_memoized_event_triggers(
            GhostSwipeable.create(**event_mapping)
        )

        component = rx.el.div(
            *children,
            **props,
        )

        var_data = VarData.merge(
            VarData(
                imports=Imports.EVENTS,
                hooks={Hooks.EVENTS: None},
            ),
            *[
                event_value._get_all_var_data()
                for event_value, _ in event_triggers.values()
            ],
            VarData(
                hooks={
                    **{
                        callback_str: None
                        for _, callback_str in event_triggers.values()
                    },
                    f"const {unique_name} = "
                    + str(
                        FunctionStringVar.create("useSwipeable").call(
                            {
                                **{
                                    to_camel_case(event_name): event_triggers[
                                        event_name
                                    ][0]
                                    for event_name in event_names
                                    if event_name in event_triggers
                                },
                                **{
                                    to_camel_case(config_name): value
                                    for config_name, value in config_mapping.items()
                                    if value is not None
                                },
                            },
                        )
                    ): None,
                },
                imports={
                    "react-swipeable": ImportVar("useSwipeable"),
                    **Imports.EVENTS,
                },
            ),
        )

        component.special_props.append(
            Var(unique_name, _var_type=dict, _var_data=var_data)
        )

        return component


def swipeable(
    *children,
    delta: float | Var[float] | None = None,
    prevent_scroll_on_swipe: bool | Var[bool] | None = None,
    track_touch: bool | Var[bool] | None = None,
    track_mouse: bool | Var[bool] | None = None,
    rotation_angle: float | Var[float] | None = None,
    swipe_duration: float | Var[float] | None = None,
    on_swiped: EventType[SwipeEvent] | EventType[()] | None = None,
    on_swiped_left: EventType[SwipeEvent] | EventType[()] | None = None,
    on_swiped_right: EventType[SwipeEvent] | EventType[()] | None = None,
    on_swiped_up: EventType[SwipeEvent] | EventType[()] | None = None,
    on_swiped_down: EventType[SwipeEvent] | EventType[()] | None = None,
    on_swiped_start: EventType[SwipeEvent] | EventType[()] | None = None,
    on_swiping: EventType[SwipeEvent] | EventType[()] | None = None,
    on_tap: EventType[()] | None = None,
    on_touch_start_or_mouse_down: EventType[()] | None = None,
    on_touch_end_or_mouse_up: EventType[()] | None = None,
    **props,
) -> rx.Component:
    """Create a swipeable component.

    Args:
        *children: The children of the component.
        delta: The min distance(px) before a swipe starts.
        prevent_scroll_on_swipe: Prevents scroll during swipe.
        track_touch: Track touch input.
        track_mouse: Track mouse input.
        rotation_angle: Set a rotation angle.
        swipe_duration: Allowable duration of a swipe (ms).
        on_swiped: After any swipe.
        on_swiped_left: After a left swipe.
        on_swiped_right: After a right swipe.
        on_swiped_up: After an up swipe.
        on_swiped_down: After a down swipe.
        on_swiped_start: After a swipe has started.
        on_swiping: While swiping.
        on_tap: After a tap.
        on_touch_start_or_mouse_down: After a touch start or mouse down.
        on_touch_end_or_mouse_up: After a touch end or mouse up.
        **props: The properties of the component.

    Returns:
        The swipeable component.
    """
    return Swipeable.create(
        *children,
        delta=delta,
        prevent_scroll_on_swipe=prevent_scroll_on_swipe,
        track_touch=track_touch,
        track_mouse=track_mouse,
        rotation_angle=rotation_angle,
        swipe_duration=swipe_duration,
        on_swiped=on_swiped,
        on_swiped_left=on_swiped_left,
        on_swiped_right=on_swiped_right,
        on_swiped_up=on_swiped_up,
        on_swiped_down=on_swiped_down,
        on_swiped_start=on_swiped_start,
        on_swiping=on_swiping,
        on_tap=on_tap,
        on_touch_start_or_mouse_down=on_touch_start_or_mouse_down,
        on_touch_end_or_mouse_up=on_touch_end_or_mouse_up,
        **props,
    )
