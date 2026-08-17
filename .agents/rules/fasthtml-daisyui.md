# FastHTML & DaisyUI Component Guidelines

These rules govern UI component construction, styling, SVG imports, and testing in FastHTML.

---

## 1. DaisyUI Component Guidelines

* **Card Parameter Integrity**: Always invoke `Card` components with `Card(title, content, **kwargs)`. Avoid passing content as the first argument to prevent header layout bugs.
* **Complex Card Headers**: If a card header requires inline forms, action buttons, or flex positioning, pass a `Div` container containing the components directly as the `title` argument.
* **DaisyUI Tooltips**: Implement tooltips with `cls="tooltip tooltip-<position>"` and `data_tip="..."`. FastHTML automatically maps `data_tip` to `data-tip`.
* **SVG Component Imports**: Import custom SVG elements (`Svg`, `Circle`, `Line`, `Text as SvgText`) exclusively from `fasthtml.svg` to prevent namespace collisions.
* **Dynamic Modal Backdrops**: Dynamic HTMX-injected `<dialog>` elements bypass native `.showModal()` backdrop triggers; always style the close-trigger form backdrop container with explicit background dimming and blur classes (e.g. `modal-backdrop bg-black/60 backdrop-blur-sm`).
* **Active Tabs Styling**: Active tabs in tab groups should scale up and receive depth: `tab-active !bg-primary !text-primary-content font-extrabold shadow-xl shadow-primary/40 scale-[1.05] border border-primary/30 z-10`.
* **Responsive Grid Column Calculation**: When computing column counts dynamically in JavaScript for FastHTML grid layouts, divide the container client width by `(min_tile_width + grid_gap)` (e.g., `Math.floor((clientWidth + gap) / (min_tile_width + gap))`), matching the exact CSS Grid `minmax(...)` specification.

---

## 2. FastHTML Testing & Route Handling

* **FastHTML Test Assertions**: When asserting HTML output or testing rendered components in pytest, always use `to_xml(response)` from `fasthtml.common` instead of `str(response)` to ensure tags and child nodes are fully compiled.
* **Decorator Signature Preservation**: Any custom decorator applied below `@rt(...)` must explicitly preserve the original function signature:
  ```python
  import functools, inspect

  def custom_decorator(f):
      @functools.wraps(f)
      def wrapper(*args, **kwargs):
          return f(*args, **kwargs)
      wrapper.__signature__ = inspect.signature(f)
      return wrapper
  ```
