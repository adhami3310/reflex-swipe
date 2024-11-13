# Reflex Swipe

Detects swipes on the page. Wraps `react-swipeable`.

```python
from reflex_swipe import swipeable

def index():
    return swipeable(
        "Swipe Here",
        on_swiped_left=rx.console_log("Swiped Left"),
        height="100px",
        width="100px",
    )
```

## Supported Props

| Prop Name               | Prop Type | Description                                 |
|-------------------------|-----------|---------------------------------------------|
| delta                   | float     | The min distance(px) before a swipe starts. |
| prevent_scroll_on_swipe | bool      | Prevents scroll during swipe.               |
| track_touch             | bool      | Track touch input.                          |
| track_mouse             | bool      | Track mouse input.                          |
| rotation_angle          | float     | Set a rotation angle.                       |
| swipe_duration          | float     | Allowable duration of a swipe (ms).         |

## Supported Events

| Event Name                   | Event Type          |
|------------------------------|---------------------|
| on_swiped                    | (SwipeEvent) -> Any |
| on_swiped_left               | (SwipeEvent) -> Any |
| on_swiped_right              | (SwipeEvent) -> Any |
| on_swiped_up                 | (SwipeEvent) -> Any |
| on_swiped_down               | (SwipeEvent) -> Any |
| on_swiped_start              | (SwipeEvent) -> Any |
| on_swiping                   | (SwipeEvent) -> Any |
| on_tap                       | () -> Any           |
| on_touch_start_or_mouse_down | () -> Any           |
| on_touch_end_or_mouse_up     | () -> Any           |

`SwipeEvent` is the following:

```python
class SwipeEvent(TypedDict):
    """A swipe event."""

    # direction of swipe
    dir: Literal["Left", "Right", "Up", "Down"]
    # initial swipe [x,y]
    initial: Tuple[float, float]
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
    vxvy: Tuple[float, float]
```