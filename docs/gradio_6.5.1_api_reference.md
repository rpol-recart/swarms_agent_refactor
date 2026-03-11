# Gradio 6.5.1 -- Complete API Reference

## 1. Package Structure

**Package location:** `/usr/local/lib/python3.11/dist-packages/gradio/`

**Top-level modules and directories:**

| Module/Directory | Purpose |
|---|---|
| `__init__.py` | Public API exports |
| `blocks.py` | `Block`, `BlockContext`, `Blocks` classes |
| `interface.py` | `Interface`, `TabbedInterface` |
| `chat_interface.py` | `ChatInterface` |
| `components/` | All UI components (40+ files) |
| `layouts/` | Layout containers (Row, Column, Tabs, Accordion, Group, Sidebar, Draggable, Walkthrough) |
| `themes/` | Theme system (Base, Default, Soft, Monochrome, Glass, Citrus, Ocean, Origin) |
| `events.py` | Event system, `Dependency`, `EventData` subclasses |
| `flagging.py` | `FlaggingCallback`, `CSVLogger`, `SimpleCSVLogger` |
| `helpers.py` | `Progress`, `Examples`, `Info`, `Warning`, `Success`, `skip`, `update` |
| `routes.py` | FastAPI app, `mount_gradio_app`, `Request` |
| `queueing.py` | Queue system |
| `data_classes.py` | Data models (`FileData`, etc.) |
| `processing_utils.py` | File/media processing utilities |
| `image_utils.py` | Image processing utilities |
| `networking.py` | Network utilities |
| `tunneling.py` | Share tunnel management |
| `analytics.py` | Telemetry |
| `context.py` | Context management for nested Blocks |
| `state_holder.py` | `SessionState`, `StateHolder` |
| `external.py` | `load()`, `load_chat()`, `load_openapi()` |
| `renderable.py` | `@gr.render` decorator |
| `mcp.py` | MCP server integration |
| `oauth.py` | OAuth support (`OAuthProfile`, `OAuthToken`) |
| `i18n.py` | Internationalization (`I18n`, `I18nData`) |
| `media.py` | `get_audio`, `get_image`, `get_video`, `get_file`, `get_model3d` |
| `validators.py` | Input validation utilities |
| `block_function.py` | `BlockFunction` wrapper |
| `component_meta.py` | Component metaclass |
| `templates.py` | Template components (Files, Mic, Sketchpad, etc.) |
| `pipelines.py` | HuggingFace pipeline integration |
| `monitoring_dashboard.py` | Monitoring dashboard |

---

## 2. Core API -- gr.Interface

```python
class Interface(Blocks):
    def __init__(
        self,
        fn: Callable,
        inputs: str | Component | Sequence[str | Component] | None,
        outputs: str | Component | Sequence[str | Component] | None,
        examples: list[Any] | list[list[Any]] | str | None = None,
        *,
        cache_examples: bool | None = None,
        cache_mode: Literal["eager", "lazy"] | None = None,
        examples_per_page: int = 10,
        example_labels: list[str] | None = None,
        preload_example: int | Literal[False] = 0,
        live: bool = False,
        title: str | I18nData | None = None,
        description: str | None = None,
        article: str | None = None,
        flagging_mode: Literal["never", "auto", "manual"] | None = None,
        flagging_options: list[str] | list[tuple[str, str]] | None = None,
        flagging_dir: str = ".gradio/flagged",
        flagging_callback: FlaggingCallback | None = None,
        analytics_enabled: bool | None = None,
        batch: bool = False,
        max_batch_size: int = 4,
        api_visibility: Literal["public", "private", "undocumented"] = "public",
        api_name: str | None = None,
        api_description: str | None | Literal[False] = None,
        _api_mode: bool = False,
        allow_duplication: bool = False,
        concurrency_limit: int | None | Literal["default"] = "default",
        additional_inputs: str | Component | Sequence[str | Component] | None = None,
        additional_inputs_accordion: str | Accordion | None = None,
        submit_btn: str | Button = "Submit",
        stop_btn: str | Button = "Stop",
        clear_btn: str | Button | None = "Clear",
        delete_cache: tuple[int, int] | None = None,
        show_progress: Literal["full", "minimal", "hidden"] = "full",
        fill_width: bool = False,
        time_limit: int | None = 30,
        stream_every: float = 0.5,
        deep_link: str | DeepLinkButton | bool | None = None,
        validator: Callable | None = None,
        **kwargs,
    )
```

**Key parameters:**
- `fn` -- The function to wrap. Each parameter maps to an input component; return values map to output components.
- `inputs`/`outputs` -- Components or string shortcuts (`"text"`, `"image"`, `"audio"`, `"label"`, etc.).
- `live` -- If True, the interface re-runs automatically when inputs change.
- `batch` -- If True, `fn` receives lists of inputs and must return tuples of lists.
- `additional_inputs` -- Extra components rendered in a collapsible accordion.
- `time_limit` / `stream_every` -- For streaming interfaces with `streaming=True` input components.
- `deep_link` -- Creates shareable URLs that preserve component state.
- `validator` -- Pre-submission validation function.

**Class method:**
```python
@classmethod
def from_pipeline(cls, pipeline: Pipeline | DiffusionPipeline, **kwargs) -> Interface
```

**Usage example:**
```python
import gradio as gr

def greet(name, intensity):
    return "Hello, " + name + "!" * int(intensity)

demo = gr.Interface(
    fn=greet,
    inputs=["text", gr.Slider(1, 10, value=3)],
    outputs="text",
    title="Greeter",
    live=False,
)
demo.launch()
```

---

## 3. Core API -- gr.Blocks

```python
class Blocks(BlockContext, BlocksEvents, metaclass=BlocksMeta):
    def __init__(
        self,
        analytics_enabled: bool | None = None,
        mode: str = "blocks",
        title: str | I18nData = "Gradio",
        fill_height: bool = False,
        fill_width: bool = False,
        delete_cache: tuple[int, int] | None = None,
        **kwargs,
    )
```

### Blocks.launch()

```python
def launch(
    self,
    inline: bool | None = None,
    inbrowser: bool = False,
    share: bool | None = None,
    debug: bool = False,
    max_threads: int = 40,
    auth: Callable[[str, str], bool] | tuple[str, str] | list[tuple[str, str]] | None = None,
    auth_message: str | None = None,
    prevent_thread_lock: bool = False,
    show_error: bool = False,
    server_name: str | None = None,
    server_port: int | None = None,
    *,
    height: int = 500,
    width: int | str = "100%",
    favicon_path: str | Path | None = None,
    ssl_keyfile: str | None = None,
    ssl_certfile: str | None = None,
    ssl_keyfile_password: str | None = None,
    ssl_verify: bool = True,
    quiet: bool = False,
    footer_links: list[Literal['api', 'gradio', 'settings'] | dict[str, str]] | None = None,
    allowed_paths: list[str] | None = None,
    blocked_paths: list[str] | None = None,
    root_path: str | None = None,
    app_kwargs: dict[str, Any] | None = None,
    state_session_capacity: int = 10000,
    share_server_address: str | None = None,
    share_server_protocol: Literal['http', 'https'] | None = None,
    share_server_tls_certificate: str | None = None,
    auth_dependency: Callable[[fastapi.Request], str | None] | None = None,
    max_file_size: str | int | None = None,
    enable_monitoring: bool | None = None,
    strict_cors: bool = True,
    node_server_name: str | None = None,
    node_port: int | None = None,
    ssr_mode: bool | None = None,
    pwa: bool | None = None,
    mcp_server: bool | None = None,
    _frontend: bool = True,
    i18n: I18n | None = None,
    theme: Theme | str | None = None,
    css: str | None = None,
    css_paths: str | Path | Sequence[str | Path] | None = None,
    js: str | Literal[True] | None = None,
    head: str | None = None,
    head_paths: str | Path | Sequence[str | Path] | None = None,
) -> tuple[App, str, str]
```

**Key launch parameters:**
- `share=True` -- Creates a public URL via Gradio's tunneling service.
- `auth` -- Username/password tuple, list of tuples, or callable for authentication.
- `auth_dependency` -- FastAPI-based auth via request headers.
- `server_name` / `server_port` -- Bind address (default `"0.0.0.0"` / `7860`).
- `ssl_keyfile` / `ssl_certfile` -- Enable HTTPS.
- `allowed_paths` / `blocked_paths` -- Control file system access.
- `max_file_size` -- Limit upload size (e.g. `"5mb"`).
- `ssr_mode` -- Server-side rendering mode.
- `pwa` -- Progressive Web App mode.
- `mcp_server` -- Enable MCP (Model Context Protocol) server.
- `theme` -- Theme object or string name (e.g. `"soft"`).
- `css` / `js` / `head` -- Custom CSS, JavaScript, or HTML head content.

### Blocks.queue()

```python
def queue(
    self,
    status_update_rate: float | Literal['auto'] = 'auto',
    api_open: bool | None = None,
    max_size: int | None = None,
    *,
    default_concurrency_limit: int | None | Literal['not_set'] = 'not_set',
)
```

- `status_update_rate` -- How often (seconds) the queue status is sent to clients.
- `max_size` -- Maximum number of requests in the queue. None = unlimited.
- `default_concurrency_limit` -- Default max concurrent executions per event (default: 1).

### Blocks events

Blocks supports the `.load()` event, which triggers when the page loads:
```python
with gr.Blocks() as demo:
    gr.Markdown("Loading...")
    demo.load(fn=my_init_fn, inputs=None, outputs=output_component)
```

**Usage pattern:**
```python
import gradio as gr

with gr.Blocks(title="My App", fill_height=True) as demo:
    with gr.Row():
        inp = gr.Textbox(label="Input")
        out = gr.Textbox(label="Output")
    btn = gr.Button("Submit")
    btn.click(fn=lambda x: x.upper(), inputs=inp, outputs=out)

demo.launch()
```

---

## 4. Core API -- gr.ChatInterface

```python
class ChatInterface(Blocks):
    def __init__(
        self,
        fn: Callable,
        *,
        multimodal: bool = False,
        chatbot: Chatbot | None = None,
        textbox: Textbox | MultimodalTextbox | None = None,
        additional_inputs: str | Component | list[str | Component] | None = None,
        additional_inputs_accordion: str | Accordion | None = None,
        additional_outputs: Component | list[Component] | None = None,
        editable: bool = False,
        examples: list[str] | list[MultimodalValue] | list[list] | None = None,
        example_labels: list[str] | None = None,
        example_icons: list[str] | None = None,
        run_examples_on_click: bool = True,
        cache_examples: bool | None = None,
        cache_mode: Literal["eager", "lazy"] | None = None,
        title: str | I18nData | None = None,
        description: str | None = None,
        flagging_mode: Literal["never", "manual"] | None = None,
        flagging_options: list[str] | tuple[str, ...] | None = ("Like", "Dislike"),
        flagging_dir: str = ".gradio/flagged",
        analytics_enabled: bool | None = None,
        autofocus: bool = True,
        autoscroll: bool = True,
        submit_btn: str | bool | None = True,
        stop_btn: str | bool | None = True,
        concurrency_limit: int | None | Literal["default"] = "default",
        delete_cache: tuple[int, int] | None = None,
        show_progress: Literal["full", "minimal", "hidden"] = "minimal",
        fill_height: bool = True,
        fill_width: bool = False,
        api_name: str | None = None,
        api_description: str | None | Literal[False] = None,
        api_visibility: Literal["public", "private", "undocumented"] = "public",
        save_history: bool = False,
        validator: Callable | None = None,
    )
```

**Key parameters:**
- `fn` -- Takes `(message, history)` where `message` is a `str` (or `dict` with `"text"` and `"files"` keys if `multimodal=True`) and `history` is a list of OpenAI-style dicts `{"role": "user"|"assistant", "content": ...}`. Returns/yields a `str`, component, dict, or list of messages.
- `multimodal` -- Enables file uploads in the textbox.
- `editable` -- Users can edit past messages to regenerate.
- `save_history` -- Saves chat history to browser local storage with a side panel for past conversations.
- `additional_outputs` -- Extra components the chat function can return values for (e.g., artifacts).
- `flagging_options` -- `"Like"` and `"Dislike"` render as thumbs up/down icons.

**Usage examples:**

Simple chatbot:
```python
import gradio as gr

def echo(message, history):
    return message

demo = gr.ChatInterface(fn=echo, title="Echo Bot")
demo.launch()
```

Streaming chatbot:
```python
import gradio as gr
import time

def slow_echo(message, history):
    for i in range(len(message)):
        time.sleep(0.05)
        yield message[: i + 1]

demo = gr.ChatInterface(fn=slow_echo)
demo.launch()
```

Multimodal chatbot with additional inputs:
```python
import gradio as gr

def respond(message, history, system_prompt, temperature):
    # message is {"text": "...", "files": [...]}
    return f"You said: {message['text']} (temp={temperature})"

demo = gr.ChatInterface(
    fn=respond,
    multimodal=True,
    additional_inputs=[
        gr.Textbox("You are a helpful assistant.", label="System Prompt"),
        gr.Slider(0, 2, value=0.7, label="Temperature"),
    ],
)
demo.launch()
```

---

## 5. Components

### Complete List of All Available Components

**Input/Output Components:**

| Component | String Shortcut | Description |
|---|---|---|
| `gr.Textbox` | `"text"`, `"textbox"` | Text input/output |
| `gr.Number` | `"number"` | Numeric input/output |
| `gr.Slider` | `"slider"` | Slider for numeric ranges |
| `gr.Checkbox` | `"checkbox"` | Boolean checkbox |
| `gr.CheckboxGroup` | `"checkboxgroup"` | Multiple checkboxes |
| `gr.Radio` | `"radio"` | Radio buttons |
| `gr.Dropdown` | `"dropdown"` | Dropdown selection |
| `gr.Image` | `"image"` | Image upload/display |
| `gr.ImageEditor` | -- | Image editing with brushes/layers |
| `gr.ImageSlider` | -- | Before/after image comparison |
| `gr.Audio` | `"audio"` | Audio upload/record/play |
| `gr.Video` | `"video"` | Video upload/record/play |
| `gr.File` | `"file"` | File upload/download |
| `gr.DataFrame` | `"dataframe"` | Tabular data |
| `gr.Gallery` | `"gallery"` | Image gallery |
| `gr.Chatbot` | `"chatbot"` | Chat message display |
| `gr.Code` | -- | Code editor with syntax highlighting |
| `gr.Markdown` | `"markdown"` | Rendered markdown |
| `gr.HTML` | `"html"` | Raw HTML |
| `gr.JSON` | `"json"` | JSON viewer |
| `gr.Label` | `"label"` | Classification label with confidences |
| `gr.HighlightedText` | `"highlightedtext"` | Text with colored spans |
| `gr.Plot` | `"plot"` | Matplotlib/Plotly/Bokeh plots |
| `gr.Model3D` | `"model3d"` | 3D model viewer |
| `gr.ColorPicker` | `"colorpicker"` | Color selection |
| `gr.DateTime` | -- | Date/time picker |
| `gr.FileExplorer` | -- | File system browser |
| `gr.MultimodalTextbox` | -- | Text + file upload combined |
| `gr.AnnotatedImage` | -- | Image with labeled regions |
| `gr.BarPlot` | -- | Bar chart (native) |
| `gr.LinePlot` | -- | Line chart (native) |
| `gr.ScatterPlot` | -- | Scatter chart (native) |

**Action Components:**

| Component | Description |
|---|---|
| `gr.Button` | Clickable button |
| `gr.UploadButton` | Upload-triggering button |
| `gr.DownloadButton` | Download-triggering button |
| `gr.ClearButton` | Clears specified components |
| `gr.DuplicateButton` | "Duplicate on HF Spaces" button |
| `gr.DeepLinkButton` | Creates shareable deep links |
| `gr.LoginButton` | OAuth login button |

**Special Components:**

| Component | Description |
|---|---|
| `gr.State` | Session state (hidden, server-side) |
| `gr.BrowserState` | Client-side persistent state (localStorage) |
| `gr.Timer` | Periodic trigger |
| `gr.Dataset` | Example dataset display |
| `gr.Navbar` | Navigation bar |
| `gr.Dialogue` | Dialog/modal popup |
| `gr.ParamViewer` | Parameter documentation viewer |

### Key Component Constructor Signatures

#### gr.Textbox
```python
Textbox(
    value: str | I18nData | Callable | None = None,
    *,
    type: Literal['text', 'password', 'email'] = 'text',
    lines: int = 1,
    max_lines: int | None = None,
    placeholder: str | I18nData | None = None,
    label: str | I18nData | None = None,
    info: str | I18nData | None = None,
    every: Timer | float | None = None,
    inputs: Component | Sequence[Component] | set[Component] | None = None,
    show_label: bool | None = None,
    container: bool = True,
    scale: int | None = None,
    min_width: int = 160,
    interactive: bool | None = None,
    visible: bool | Literal['hidden'] = True,
    elem_id: str | None = None,
    autofocus: bool = False,
    autoscroll: bool = True,
    elem_classes: list[str] | str | None = None,
    render: bool = True,
    key: int | str | tuple[int | str, ...] | None = None,
    preserved_by_key: list[str] | str | None = 'value',
    text_align: Literal['left', 'right'] | None = None,
    rtl: bool = False,
    buttons: list[Literal['copy'] | Button] | None = None,
    max_length: int | None = None,
    submit_btn: str | bool | None = False,
    stop_btn: str | bool | None = False,
    html_attributes: InputHTMLAttributes | None = None,
)
```
Events: `change`, `input`, `select`, `submit`, `focus`, `blur`, `stop`, `copy`

#### gr.Image
```python
Image(
    value: str | PIL.Image.Image | np.ndarray | Callable | None = None,
    *,
    format: str = 'webp',
    height: int | str | None = None,
    width: int | str | None = None,
    image_mode: Literal['1','L','P','RGB','RGBA','CMYK','YCbCr','LAB','HSV','I','F'] | None = 'RGB',
    sources: list[Literal['upload','webcam','clipboard']] | Literal['upload','webcam','clipboard'] | None = None,
    type: Literal['numpy', 'pil', 'filepath'] = 'numpy',
    label: str | I18nData | None = None,
    every: Timer | float | None = None,
    inputs: Component | Sequence[Component] | set[Component] | None = None,
    show_label: bool | None = None,
    buttons: list[Literal['download','share','fullscreen'] | Button] | None = None,
    container: bool = True,
    scale: int | None = None,
    min_width: int = 160,
    interactive: bool | None = None,
    visible: bool | Literal['hidden'] = True,
    streaming: bool = False,
    elem_id: str | None = None,
    elem_classes: list[str] | str | None = None,
    render: bool = True,
    key: int | str | tuple[int | str, ...] | None = None,
    preserved_by_key: list[str] | str | None = 'value',
    webcam_options: WebcamOptions | None = None,
    placeholder: str | None = None,
    watermark: WatermarkOptions | None = None,
)
```
Events: `clear`, `change`, `stream`, `select`, `upload`, `input`

#### gr.Audio
```python
Audio(
    value: str | Path | tuple[int, np.ndarray] | Callable | None = None,
    *,
    sources: list[Literal['upload','microphone']] | Literal['upload','microphone'] | None = None,
    type: Literal['numpy', 'filepath'] = 'numpy',
    label: str | I18nData | None = None,
    every: Timer | float | None = None,
    inputs: Component | Sequence[Component] | set[Component] | None = None,
    show_label: bool | None = None,
    container: bool = True,
    scale: int | None = None,
    min_width: int = 160,
    interactive: bool | None = None,
    visible: bool | Literal['hidden'] = True,
    streaming: bool = False,
    elem_id: str | None = None,
    elem_classes: list[str] | str | None = None,
    render: bool = True,
    key: int | str | tuple[int | str, ...] | None = None,
    preserved_by_key: list[str] | str | None = 'value',
    format: Literal['wav', 'mp3'] | None = None,
    autoplay: bool = False,
    editable: bool = True,
    buttons: list[Literal['download','share'] | Button] | None = None,
    waveform_options: WaveformOptions | dict | None = None,
    loop: bool = False,
    recording: bool = False,
    subtitles: str | Path | list[dict[str, Any]] | None = None,
    playback_position: float = 0,
)
```
Events: `stream`, `change`, `clear`, `play`, `pause`, `stop`, `start_recording`, `pause_recording`, `stop_recording`, `upload`, `input`

#### gr.Slider
```python
Slider(
    minimum: float = 0,
    maximum: float = 100,
    value: float | Callable | None = None,
    *,
    step: float | None = None,
    precision: int | None = None,
    label: str | I18nData | None = None,
    info: str | I18nData | None = None,
    every: Timer | float | None = None,
    inputs: Component | Sequence[Component] | set[Component] | None = None,
    show_label: bool | None = None,
    container: bool = True,
    scale: int | None = None,
    min_width: int = 160,
    interactive: bool | None = None,
    visible: bool | Literal['hidden'] = True,
    elem_id: str | None = None,
    elem_classes: list[str] | str | None = None,
    render: bool = True,
    key: int | str | tuple[int | str, ...] | None = None,
    preserved_by_key: list[str] | str | None = 'value',
    randomize: bool = False,
    buttons: list[Literal['reset']] | None = None,
)
```
Events: `change`, `input`, `release`

#### gr.Dropdown
```python
Dropdown(
    choices: Sequence[str | int | float | tuple[str, str | int | float]] | None = None,
    *,
    value: str | int | float | Sequence[str | int | float] | Callable | DefaultValue | None = <default>,
    type: Literal['value', 'index'] = 'value',
    multiselect: bool | None = None,
    allow_custom_value: bool = False,
    max_choices: int | None = None,
    filterable: bool = True,
    label: str | I18nData | None = None,
    info: str | I18nData | None = None,
    every: Timer | float | None = None,
    inputs: Component | Sequence[Component] | set[Component] | None = None,
    show_label: bool | None = None,
    container: bool = True,
    scale: int | None = None,
    min_width: int = 160,
    interactive: bool | None = None,
    visible: bool | Literal['hidden'] = True,
    elem_id: str | None = None,
    elem_classes: list[str] | str | None = None,
    render: bool = True,
    key: int | str | tuple[int | str, ...] | None = None,
    preserved_by_key: list[str] | str | None = 'value',
    buttons: list[Button] | None = None,
)
```
Events: `change`, `input`, `select`, `focus`, `blur`, `key_up`

#### gr.File
```python
File(
    value: str | list[str] | Callable | None = None,
    *,
    file_count: Literal['single', 'multiple', 'directory'] = 'single',
    file_types: list[str] | None = None,
    type: Literal['filepath', 'binary'] = 'filepath',
    label: str | I18nData | None = None,
    every: Timer | float | None = None,
    inputs: Component | Sequence[Component] | set[Component] | None = None,
    show_label: bool | None = None,
    container: bool = True,
    scale: int | None = None,
    min_width: int = 160,
    height: int | str | float | None = None,
    interactive: bool | None = None,
    visible: bool | Literal['hidden'] = True,
    elem_id: str | None = None,
    elem_classes: list[str] | str | None = None,
    render: bool = True,
    key: int | str | tuple[int | str, ...] | None = None,
    preserved_by_key: list[str] | str | None = 'value',
    allow_reordering: bool = False,
    buttons: list[Button] | None = None,
)
```
Events: `change`, `select`, `clear`, `upload`, `delete`, `download`

#### gr.DataFrame
```python
Dataframe(
    value: pd.DataFrame | Styler | np.ndarray | pl.DataFrame | list | list[list] | dict | str | Callable | None = None,
    *,
    headers: list[str] | None = None,
    row_count: int | None = None,
    row_limits: tuple[int | None, int | None] | None = None,
    col_count: None = None,
    column_count: int | None = None,
    column_limits: tuple[int | None, int | None] | None = None,
    datatype: Literal['str','number','bool','date','markdown','html','image','auto'] | Sequence[...] = 'str',
    type: Literal['pandas', 'numpy', 'array', 'polars'] = 'pandas',
    latex_delimiters: list[dict[str, str | bool]] | None = None,
    label: str | I18nData | None = None,
    show_label: bool | None = None,
    every: Timer | float | None = None,
    inputs: Component | Sequence[Component] | set[Component] | None = None,
    max_height: int | str = 500,
    scale: int | None = None,
    min_width: int = 160,
    interactive: bool | None = None,
    visible: bool | Literal['hidden'] = True,
    elem_id: str | None = None,
    elem_classes: list[str] | str | None = None,
    render: bool = True,
    key: int | str | tuple[int | str, ...] | None = None,
    preserved_by_key: list[str] | str | None = 'value',
    wrap: bool = False,
    line_breaks: bool = True,
    column_widths: list[str | int] | None = None,
    buttons: list[Literal['fullscreen', 'copy']] | None = None,
    show_row_numbers: bool = False,
    max_chars: int | None = None,
    show_search: Literal['none', 'search', 'filter'] = 'none',
    pinned_columns: int | None = None,
    static_columns: list[int] | None = None,
)
```

#### gr.Chatbot
```python
Chatbot(
    value: list[MessageDict | Message] | Callable | None = None,
    *,
    label: str | I18nData | None = None,
    every: Timer | float | None = None,
    inputs: Component | Sequence[Component] | set[Component] | None = None,
    show_label: bool | None = None,
    container: bool = True,
    scale: int | None = None,
    min_width: int = 160,
    visible: bool | Literal['hidden'] = True,
    elem_id: str | None = None,
    elem_classes: list[str] | str | None = None,
    autoscroll: bool = True,
    render: bool = True,
    key: int | str | tuple[int | str, ...] | None = None,
    preserved_by_key: list[str] | str | None = 'value',
    height: int | str | None = 400,
    resizable: bool = False,
    max_height: int | str | None = None,
    min_height: int | str | None = None,
    editable: Literal['user', 'all'] | None = None,
    latex_delimiters: list[dict[str, str | bool]] | None = None,
    rtl: bool = False,
    buttons: list[Literal['share','copy','copy_all'] | Button] | None = None,
    watermark: str | None = None,
    avatar_images: tuple[str | Path | None, str | Path | None] | None = None,
    sanitize_html: bool = True,
    render_markdown: bool = True,
    feedback_options: list[str] | tuple[str, ...] | None = ('Like', 'Dislike'),
    feedback_value: Sequence[str | None] | None = None,
    line_breaks: bool = True,
    layout: Literal['panel', 'bubble'] | None = None,
    placeholder: str | None = None,
    examples: list[ExampleMessage] | None = None,
    allow_file_downloads=True,
    group_consecutive_messages: bool = True,
    allow_tags: list[str] | bool = True,
    reasoning_tags: list[tuple[str, str]] | None = None,
    like_user_message: bool = False,
)
```
Events: `change`, `select`, `like`, `retry`, `undo`, `example_select`, `option_select`, `clear`, `copy`, `edit`

#### gr.Button
```python
Button(
    value: str | I18nData | Callable = 'Run',
    *,
    every: Timer | float | None = None,
    inputs: Component | Sequence[Component] | set[Component] | None = None,
    variant: Literal['primary', 'secondary', 'stop', 'huggingface'] = 'secondary',
    size: Literal['sm', 'md', 'lg'] = 'lg',
    icon: str | Path | None = None,
    link: str | None = None,
    link_target: Literal['_self', '_blank', '_parent', '_top'] = '_self',
    visible: bool | Literal['hidden'] = True,
    interactive: bool = True,
    elem_id: str | None = None,
    elem_classes: list[str] | str | None = None,
    render: bool = True,
    key: int | str | tuple[int | str, ...] | None = None,
    preserved_by_key: list[str] | str | None = 'value',
    scale: int | None = None,
    min_width: int | None = None,
)
```
Events: `click`

#### gr.Video
```python
Video(
    value: str | Path | Callable | None = None,
    *,
    format: str | None = None,
    sources: list[Literal['upload','webcam']] | Literal['upload','webcam'] | None = None,
    height: int | str | None = None,
    width: int | str | None = None,
    label: str | I18nData | None = None,
    every: Timer | float | None = None,
    inputs: Component | Sequence[Component] | set[Component] | None = None,
    show_label: bool | None = None,
    container: bool = True,
    scale: int | None = None,
    min_width: int = 160,
    interactive: bool | None = None,
    visible: bool | Literal['hidden'] = True,
    elem_id: str | None = None,
    elem_classes: list[str] | str | None = None,
    render: bool = True,
    key: int | str | tuple[int | str, ...] | None = None,
    preserved_by_key: list[str] | str | None = 'value',
    webcam_options: WebcamOptions | None = None,
    include_audio: bool | None = None,
    autoplay: bool = False,
    buttons: list[Literal['download','share'] | Button] | None = None,
    loop: bool = False,
    streaming: bool = False,
    watermark: WatermarkOptions | None = None,
    subtitles: str | Path | list[dict[str, Any]] | None = None,
    playback_position: float = 0,
)
```
Events: `change`, `clear`, `start_recording`, `stop_recording`, `stop`, `play`, `pause`, `end`, `upload`, `input`

#### gr.Code
```python
Code(
    value: str | Callable | None = None,
    language: Literal['python','c','cpp','markdown','latex','json','html','css',
                      'javascript','jinja2','typescript','yaml','dockerfile','shell',
                      'r','sql','sql-msSQL','sql-mySQL','sql-mariaDB','sql-sqlite',
                      'sql-cassandra','sql-plSQL','sql-hive','sql-pgSQL','sql-gql',
                      'sql-gpSQL','sql-sparkSQL','sql-esper'] | None = None,
    *,
    every: Timer | float | None = None,
    inputs: Component | Sequence[Component] | set[Component] | None = None,
    lines: int = 5,
    max_lines: int | None = None,
    label: str | I18nData | None = None,
    interactive: bool | None = None,
    show_label: bool | None = None,
    container: bool = True,
    scale: int | None = None,
    min_width: int = 160,
    visible: bool | Literal['hidden'] = True,
    elem_id: str | None = None,
    elem_classes: list[str] | str | None = None,
    render: bool = True,
    key: int | str | tuple[int | str, ...] | None = None,
    preserved_by_key: list[str] | str | None = 'value',
    wrap_lines: bool = False,
    show_line_numbers: bool = True,
    autocomplete: bool = False,
    buttons: list[Literal['copy','download'] | Button] | None = None,
)
```

---

## 6. Event Handling

### How Events Work

Every component has a set of events. You attach listeners by calling the event method on the component:

```python
component.event_name(fn, inputs, outputs)
```

This returns a `Dependency` object that can be chained.

### Event Listener Signature (all events share this)

```python
def event_trigger(
    block: Block | None,
    fn: Callable | None | Literal["decorator"] = "decorator",
    inputs: Component | BlockContext | Sequence[...] | Set[...] | None = None,
    outputs: Component | BlockContext | Sequence[...] | Set[...] | None = None,
    api_name: str | None = None,
    api_description: str | None | Literal[False] = None,
    scroll_to_output: bool = False,
    show_progress: Literal["full", "minimal", "hidden"] = <event_default>,
    show_progress_on: Component | Sequence[Component] | None = None,
    queue: bool = True,
    batch: bool = False,
    max_batch_size: int = 4,
    preprocess: bool = True,
    postprocess: bool = True,
    cancels: dict[str, Any] | list[dict[str, Any]] | None = None,
    trigger_mode: Literal["once", "multiple", "always_last"] | None = None,
    js: str | Literal[True] | None = None,
    concurrency_limit: int | None | Literal["default"] = "default",
    concurrency_id: str | None = None,
    api_visibility: Literal["public", "private", "undocumented"] = "public",
    time_limit: int | None = None,
    stream_every: float = 0.5,
    key: int | str | tuple[int | str, ...] | None = None,
    validator: Callable | None = None,
) -> Dependency
```

### Chaining Events with Dependency

Every event listener returns a `Dependency` object with three chaining methods:

```python
dep = btn.click(fn=step1, inputs=inp, outputs=out)
dep.then(fn=step2, inputs=out, outputs=out2)      # Runs after step1, regardless of success/failure
dep.success(fn=on_ok, inputs=None, outputs=status)  # Runs only if step1 succeeds
dep.failure(fn=on_err, inputs=None, outputs=status)  # Runs only if step1 fails
```

`.then()`, `.success()`, and `.failure()` each return a new `Dependency`, so they can be further chained.

### gr.on() -- Multi-trigger Events

```python
gr.on(
    triggers: Sequence[EventListenerCallable] | EventListenerCallable | None = None,
    fn: Callable[..., Any] | None | Literal['decorator'] = 'decorator',
    inputs: Component | BlockContext | Sequence[...] | Set[...] | None = None,
    outputs: Component | BlockContext | Sequence[...] | Set[...] | None = None,
    *,
    # ... same parameters as event_trigger above ...
) -> Dependency
```

Usage:
```python
gr.on(
    triggers=[btn.click, inp.submit],
    fn=process,
    inputs=inp,
    outputs=out,
)
```

### EventData Subclasses

These are used as type hints in `fn` parameters to receive event metadata:

| Class | Event | Attributes |
|---|---|---|
| `gr.EventData` | Any | `.target` |
| `gr.SelectData` | `.select()` | `.index`, `.value`, `.row_value`, `.col_value`, `.selected` |
| `gr.KeyUpData` | `.key_up()` | `.key`, `.input_value` |
| `gr.LikeData` | `.like()` | `.index`, `.value`, `.liked` |
| `gr.EditData` | `.edit()` | `.index`, `.old_value`, `.value` |
| `gr.DeletedFileData` | `.delete()` | `.file` |
| `gr.DownloadData` | `.download()` | `.file` |
| `gr.CopyData` | `.copy()` | `.value` |
| `gr.RetryData` | `.retry()` | `.index`, `.value` |
| `gr.UndoData` | `.undo()` | `.index`, `.value` |

**Example:**
```python
def on_select(evt: gr.SelectData):
    return f"Selected {evt.value} at index {evt.index}"
gallery.select(on_select, None, output_textbox)
```

### Decorator syntax

```python
@btn.click(inputs=inp, outputs=out)
def process(x):
    return x.upper()
```

---

## 7. Layout Components

### gr.Row
```python
Row(
    *,
    variant: Literal['default', 'panel', 'compact'] = 'default',
    visible: bool | Literal['hidden'] = True,
    elem_id: str | None = None,
    elem_classes: list[str] | str | None = None,
    scale: int | None = None,
    render: bool = True,
    height: int | str | None = None,
    max_height: int | str | None = None,
    min_height: int | str | None = None,
    equal_height: bool = False,
    show_progress: bool = False,
    key: int | str | tuple[int | str, ...] | None = None,
    preserved_by_key: list[str] | str | None = None,
)
```

### gr.Column
```python
Column(
    *,
    scale: int = 1,
    min_width: int = 320,
    variant: Literal['default', 'panel', 'compact'] = 'default',
    visible: bool | Literal['hidden'] = True,
    elem_id: str | None = None,
    elem_classes: list[str] | str | None = None,
    render: bool = True,
    show_progress: bool = False,
    key: int | str | tuple[int | str, ...] | None = None,
    preserved_by_key: list[str] | str | None = None,
)
```

### gr.Tab
```python
Tab(
    label: str | I18nData | None = None,
    visible: bool | Literal['hidden'] = True,
    interactive: bool = True,
    *,
    id: int | str | None = None,
    elem_id: str | None = None,
    elem_classes: list[str] | str | None = None,
    scale: int | None = None,
    render: bool = True,
    key: int | str | tuple[int | str, ...] | None = None,
    preserved_by_key: list[str] | str | None = None,
    render_children: bool = False,
)
```

### gr.Tabs
```python
Tabs(
    *,
    selected: int | str | None = None,
    visible: bool | Literal['hidden'] = True,
    elem_id: str | None = None,
    elem_classes: list[str] | str | None = None,
    render: bool = True,
    key: int | str | tuple[int | str, ...] | None = None,
    preserved_by_key: list[str] | str | None = None,
)
```

### gr.Accordion
```python
Accordion(
    label: str | I18nData | None = None,
    *,
    open: bool = True,
    visible: bool | Literal['hidden'] = True,
    elem_id: str | None = None,
    elem_classes: list[str] | str | None = None,
    render: bool = True,
    key: int | str | tuple[int | str, ...] | None = None,
    preserved_by_key: list[str] | str | None = None,
)
```

### gr.Group
```python
Group(
    *,
    visible: bool | Literal['hidden'] = True,
    elem_id: str | None = None,
    elem_classes: list[str] | str | None = None,
    render: bool = True,
    key: int | str | tuple[int | str, ...] | None = None,
    preserved_by_key: list[str] | str | None = None,
)
```

### gr.Sidebar
```python
Sidebar(
    label: str | I18nData | None = None,
    *,
    open: bool = True,
    visible: bool | Literal['hidden'] = True,
    elem_id: str | None = None,
    elem_classes: list[str] | str | None = None,
    render: bool = True,
    width: int | str = 320,
    position: Literal['left', 'right'] = 'left',
    key: int | str | tuple[int | str, ...] | None = None,
    preserved_by_key: list[str] | str | None = None,
)
```

**Layout usage example:**
```python
with gr.Blocks() as demo:
    with gr.Sidebar(label="Settings"):
        temp = gr.Slider(0, 1, label="Temperature")
    with gr.Tabs():
        with gr.Tab("Text"):
            with gr.Row():
                with gr.Column(scale=2):
                    inp = gr.Textbox()
                with gr.Column(scale=1):
                    out = gr.Textbox()
        with gr.Tab("Image"):
            img = gr.Image()
    with gr.Accordion("Advanced", open=False):
        gr.Markdown("Advanced settings here")
    with gr.Group():
        a = gr.Textbox(label="A")
        b = gr.Textbox(label="B")
```

---

## 8. State Management

### gr.State -- Server-side Session State

```python
State(
    value: Any = None,
    render: bool = True,
    *,
    time_to_live: int | float | None = None,
    delete_callback: Callable[[Any], None] | None = None,
)
```

- Stores arbitrary Python objects server-side, per session.
- Value is deepcopied for each new session.
- `time_to_live` -- Auto-delete after N seconds of inactivity.
- `delete_callback` -- Called when state is cleaned up (useful for closing connections, freeing resources).
- State is automatically cleaned up when the user closes the browser tab.
- `state_session_capacity` in `launch()` controls the max number of concurrent sessions (default 10000).

**Usage:**
```python
with gr.Blocks() as demo:
    counter = gr.State(value=0)
    btn = gr.Button("Increment")
    out = gr.Number()

    def increment(count):
        return count + 1, count + 1

    btn.click(increment, inputs=counter, outputs=[counter, out])
```

### gr.BrowserState -- Client-side Persistent State

```python
BrowserState(
    default_value: Any = None,
    *,
    storage_key: str | None = None,
    secret: str | None = None,
    render: bool = True,
)
```

- Persists data in the browser's `localStorage`.
- Survives page refreshes and browser restarts.
- `storage_key` -- Custom localStorage key (auto-generated if None).
- `secret` -- Encryption key for the stored data.

---

## 9. Theming

### Built-in Themes

| Theme Class | Description |
|---|---|
| `gr.themes.Default` | Default Gradio theme |
| `gr.themes.Soft` | Softer, rounded look |
| `gr.themes.Monochrome` | Black and white |
| `gr.themes.Glass` | Glassmorphism style |
| `gr.themes.Citrus` | Bright citrus colors |
| `gr.themes.Ocean` | Ocean blue palette |
| `gr.themes.Origin` | Original Gradio classic look |
| `gr.themes.Base` | Base class for custom themes |

### Theme Base Constructor

```python
gr.themes.Base(
    *,
    primary_hue: colors.Color | str = <blue>,
    secondary_hue: colors.Color | str = <blue>,
    neutral_hue: colors.Color | str = <gray>,
    text_size: sizes.Size | str = <text_md>,
    spacing_size: sizes.Size | str = <spacing_md>,
    radius_size: sizes.Size | str = <radius_md>,
    font: Font | str | Iterable[Font | str] = (LocalFont('IBM Plex Sans'), 'ui-sans-serif', 'system-ui', 'sans-serif'),
    font_mono: Font | str | Iterable[Font | str] = (LocalFont('IBM Plex Mono'), 'ui-monospace', 'Consolas', 'monospace'),
)
```

### Using Themes

```python
# Use a built-in theme by name
demo.launch(theme="soft")

# Or pass a theme object
demo.launch(theme=gr.themes.Soft())

# Custom theme
custom_theme = gr.themes.Base(
    primary_hue=gr.themes.colors.emerald,
    secondary_hue=gr.themes.colors.blue,
    neutral_hue=gr.themes.colors.gray,
    font=gr.themes.GoogleFont("Open Sans"),
)
demo.launch(theme=custom_theme)
```

### Theme Utilities

- `gr.themes.colors` -- Color palettes (slate, gray, zinc, neutral, stone, red, orange, amber, yellow, lime, green, emerald, teal, cyan, sky, blue, indigo, violet, purple, fuchsia, pink, rose)
- `gr.themes.sizes` -- Size presets (text_sm/md/lg, spacing_sm/md/lg, radius_sm/md/lg/none)
- `gr.themes.GoogleFont("Font Name")` -- Use Google Fonts

---

## 10. File/Media Handling

### How File Uploads Work

1. Files are uploaded to the server and stored in a temporary cache directory (`GRADIO_TEMP_DIR` or system temp).
2. Components with `type="filepath"` pass the file path to `fn`.
3. Components with `type="numpy"` (Image, Audio) convert to numpy arrays.
4. Components with `type="pil"` (Image) convert to PIL Image objects.
5. Components with `type="binary"` (File) pass raw bytes.

### Controlling File Access

- `allowed_paths` in `launch()` -- Whitelist directories the server can serve files from.
- `blocked_paths` in `launch()` -- Blacklist directories.
- `max_file_size` in `launch()` -- Limit upload size (e.g., `"10mb"`, `"1gb"`, or bytes as int).

### Cache Management

- `delete_cache=(frequency, age)` in `Blocks()` or `Interface()` -- Periodically delete temp files. Both values in seconds.
- Example: `delete_cache=(86400, 86400)` deletes files older than 1 day, checks every day.
- Cache is cleared entirely on server restart.

### gr.File specifics
- `file_count="single"` -- Returns a single filepath string.
- `file_count="multiple"` -- Returns a list of filepath strings.
- `file_count="directory"` -- Allows directory upload, returns list of paths.
- `file_types=[".pdf", ".txt"]` -- Restrict accepted file extensions.

### gr.Image specifics
- `type="numpy"` (default) -- Returns `(height, width, channels)` numpy array.
- `type="pil"` -- Returns PIL.Image object.
- `type="filepath"` -- Returns string path to temporary file.
- `format="webp"` (default) -- Output format for processed images.
- `sources=["upload", "webcam", "clipboard"]` -- Where images come from.
- `streaming=True` -- For live webcam streaming.

### gr.Audio specifics
- `type="numpy"` (default) -- Returns `(sample_rate, data)` tuple.
- `type="filepath"` -- Returns string path.
- `sources=["upload", "microphone"]` -- Input sources.
- `streaming=True` -- For live microphone streaming.
- `format="wav"` or `"mp3"` -- Output format.

### gr.Video specifics
- Always returns filepath.
- `sources=["upload", "webcam"]`.
- `streaming=True` -- For webcam streaming.
- `include_audio` -- Whether to include audio track.

### Media Utility Functions

```python
gr.get_image(url_or_path) -> PIL.Image
gr.get_audio(url_or_path) -> tuple[int, np.ndarray]
gr.get_video(url_or_path) -> str  # filepath
gr.get_file(url_or_path) -> str   # filepath
gr.get_model3d(url_or_path) -> str  # filepath
```

---

## 11. Flagging

### FlaggingCallback (Abstract Base Class)

```python
class FlaggingCallback:
    def setup(self, components: Sequence[Component], flagging_dir: str): ...
    def flag(self, flag_data: list[Any], flag_option: str | None = None, username: str | None = None) -> int: ...
```

### gr.CSVLogger

```python
CSVLogger(
    simplify_file_data: bool = True,
    verbose: bool = True,
    dataset_file_name: str | None = None,
)
```

Default flagging callback. Saves flagged data to a CSV file in `flagging_dir`.

### gr.SimpleCSVLogger

Simplified CSV logger without file handling.

### ChatCSVLogger

Used internally by `ChatInterface` for chat-specific flagging.

### Usage in Interface

```python
demo = gr.Interface(
    fn=predict,
    inputs="image",
    outputs="label",
    flagging_mode="manual",           # "never", "auto", or "manual"
    flagging_options=["Incorrect", "Offensive", "Other"],
    flagging_dir="./flagged_data",
    flagging_callback=gr.CSVLogger(),  # Default
)
```

---

## 12. API and Networking

### API Endpoints

Every event listener with `api_visibility="public"` (default) is automatically exposed as an API endpoint. The API docs are available at `<app_url>/?view=api`.

**Controlling API visibility:**
- `api_visibility="public"` -- Shown in docs, callable.
- `api_visibility="private"` -- Hidden from docs, not callable.
- `api_visibility="undocumented"` -- Hidden from docs, but callable.
- `api_name="custom_name"` -- Custom endpoint name.

### gr.mount_gradio_app -- FastAPI Integration

```python
gr.mount_gradio_app(
    app: fastapi.FastAPI,
    blocks: gradio.Blocks,
    path: str,
    server_name: str = '0.0.0.0',
    server_port: int = 7860,
    footer_links: list[...] | None = None,
    app_kwargs: dict[str, Any] | None = None,
    *,
    auth: Callable | tuple[str, str] | list[tuple[str, str]] | None = None,
    auth_message: str | None = None,
    auth_dependency: Callable[[fastapi.Request], str | None] | None = None,
    root_path: str | None = None,
    allowed_paths: list[str] | None = None,
    blocked_paths: list[str] | None = None,
    favicon_path: str | None = None,
    show_error: bool = True,
    max_file_size: str | int | None = None,
    ssr_mode: bool | None = None,
    node_server_name: str | None = None,
    node_port: int | None = None,
    enable_monitoring: bool | None = None,
    pwa: bool | None = None,
    i18n: I18n | None = None,
    mcp_server: bool | None = None,
    theme: Theme | str | None = None,
    css: str | None = None,
    css_paths: str | Path | Sequence[str | Path] | None = None,
    js: str | Literal[True] | None = None,
    head: str | None = None,
    head_paths: str | Path | Sequence[str | Path] | None = None,
) -> fastapi.FastAPI
```

**Usage:**
```python
import fastapi
import gradio as gr

app = fastapi.FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

with gr.Blocks() as demo:
    gr.Textbox(label="Hello")

app = gr.mount_gradio_app(app, demo, path="/gradio")
# Run with: uvicorn app:app
```

### Sharing (share=True)

```python
demo.launch(share=True)
# Creates a public URL like https://xxxxx.gradio.live
# Valid for 72 hours
```

Share parameters on `launch()`:
- `share_server_address` -- Custom share server.
- `share_server_protocol` -- `"http"` or `"https"`.
- `share_server_tls_certificate` -- Custom TLS cert.

### Authentication

```python
# Simple username/password
demo.launch(auth=("admin", "password123"))

# Multiple users
demo.launch(auth=[("user1", "pass1"), ("user2", "pass2")])

# Custom auth function
def auth_fn(username, password):
    return username == "admin" and password == "secret"
demo.launch(auth=auth_fn, auth_message="Please log in")

# FastAPI dependency-based auth
def check_auth(request: fastapi.Request):
    token = request.headers.get("Authorization")
    if token == "Bearer valid_token":
        return "authenticated_user"
    return None
demo.launch(auth_dependency=check_auth)
```

### OAuth

```python
from gradio import OAuthProfile, OAuthToken, LoginButton

with gr.Blocks() as demo:
    login = gr.LoginButton()
    # In your fn, add OAuthProfile as type hint to get user info
    def greet(profile: gr.OAuthProfile | None):
        if profile:
            return f"Hello, {profile.name}!"
        return "Please log in"
```

### MCP Server

```python
demo.launch(mcp_server=True)  # Exposes API endpoints as MCP tools
```

### gr.load / gr.load_chat / gr.load_openapi

```python
# Load a Hugging Face model as a demo
demo = gr.load("huggingface/gpt2")

# Load a chat model
demo = gr.load_chat("huggingface/meta-llama/Llama-2-7b-chat-hf")

# Load from OpenAPI spec
demo = gr.load_openapi("https://api.example.com/openapi.json")
```

---

## 13. Streaming

### Text Streaming (Generator Functions)

Any function that `yield`s values instead of returning them will stream output:

```python
import gradio as gr
import time

def stream_text(text):
    output = ""
    for char in text:
        output += char
        yield output
        time.sleep(0.05)

demo = gr.Interface(fn=stream_text, inputs="text", outputs="text")
demo.launch()
```

### Media Streaming

For live webcam/microphone streaming:

```python
# Image streaming from webcam
demo = gr.Interface(
    fn=process_frame,
    inputs=gr.Image(sources=["webcam"], streaming=True),
    outputs="image",
    live=True,
    time_limit=30,
    stream_every=0.5,
)

# Audio streaming from microphone
demo = gr.Interface(
    fn=process_audio,
    inputs=gr.Audio(sources=["microphone"], streaming=True),
    outputs="audio",
    live=True,
)
```

### Streaming in ChatInterface

`ChatInterface` natively supports generators:

```python
def chat(message, history):
    response = ""
    for word in message.split():
        response += word + " "
        yield response
        time.sleep(0.1)

demo = gr.ChatInterface(fn=chat)
```

### Event-level streaming parameters

- `stream_every: float = 0.5` -- How often (seconds) to send stream chunks to client.
- `time_limit: int | None = None` -- Maximum streaming duration in seconds.

---

## 14. gr.Progress

```python
class Progress(Iterable):
    def __init__(self, track_tqdm: bool = False)
```

Add as a parameter with default value in your function:

```python
import gradio as gr
import time

def my_function(x, progress=gr.Progress()):
    progress(0, desc="Starting...")
    time.sleep(1)
    for i in progress.tqdm(range(100)):
        time.sleep(0.1)
    return x

demo = gr.Interface(my_function, gr.Textbox(), gr.Textbox())
demo.launch()
```

**Key methods:**
- `progress(fraction, desc="...")` -- Update progress bar. `fraction` is 0.0 to 1.0.
- `progress.tqdm(iterable, desc="...")` -- Wrap an iterable for automatic progress tracking.
- `track_tqdm=True` -- Automatically tracks any `tqdm.tqdm` calls within the function.

**Note:** Progress is not displayed for cached examples.

---

## 15. JavaScript Integration

### js parameter in events

Run JavaScript before the Python function:

```python
btn.click(
    fn=python_fn,
    inputs=inp,
    outputs=out,
    js="(x) => x.toUpperCase()"  # Runs in browser before server call
)
```

The JS function receives the input values and its return value is passed to the Python `fn`.

### js parameter with True

```python
btn.click(
    fn=None,
    inputs=inp,
    outputs=out,
    js=True  # Uses Groovy transpilation
)
```

### Custom JS on page load

```python
with gr.Blocks(js="alert('Page loaded!')") as demo:
    ...
demo.launch()

# Or via launch:
demo.launch(js="() => { console.log('App started'); }")
```

### Custom head content

```python
demo.launch(
    head="<script src='https://cdn.example.com/lib.js'></script>"
)
```

### gr.HTML js_on_load

```python
gr.HTML(
    value="<div>Hello</div>",
    js_on_load="element.addEventListener('click', function() { trigger('click') });"
)
```

---

## 16. Queueing

The queue is enabled by default. It manages concurrent requests and provides:

1. **Concurrency control** -- Limits simultaneous executions per event.
2. **Request ordering** -- FIFO processing.
3. **Status updates** -- Clients see their position in queue.

### Configuration

```python
demo.queue(
    status_update_rate="auto",        # or float (seconds)
    api_open=None,                    # Whether API is open (None = follows queue)
    max_size=None,                    # Max queue length (None = unlimited)
    default_concurrency_limit="not_set",  # Default per-event limit (1 if not set)
)
```

### Per-event concurrency

```python
btn.click(
    fn=expensive_fn,
    inputs=inp,
    outputs=out,
    concurrency_limit=2,        # Max 2 simultaneous runs of this event
    concurrency_id="gpu_tasks",  # Share limit with other events in same group
)
```

### Cancellation

```python
click_event = btn.click(fn=long_fn, inputs=inp, outputs=out)
cancel_btn.click(fn=None, inputs=None, outputs=None, cancels=[click_event])
```

---

## 17. gr.Examples

```python
gr.Examples(
    examples: list[Any] | list[list[Any]] | str,
    inputs: Component | Sequence[Component],
    outputs: Component | Sequence[Component] | None = None,
    fn: Callable | None = None,
    cache_examples: bool | None = None,
    cache_mode: Literal["eager", "lazy"] | None = None,
    examples_per_page: int = 10,
    label: str | I18nData | None = None,
    elem_id: str | None = None,
    run_on_click: bool = False,
    preprocess: bool = True,
    postprocess: bool = True,
    api_visibility: Literal["public", "private", "undocumented"] = "undocumented",
    api_name: str | None = "load_example",
    api_description: str | None | Literal[False] = None,
    batch: bool = False,
    *,
    example_labels: list[str] | None = None,
    visible: bool | Literal["hidden"] = True,
    preload: int | Literal[False] = 0,
)
```

**Key parameters:**
- `examples` -- List of example values (single input) or list of lists (multiple inputs). Can also be a directory path containing example files.
- `inputs` -- The component(s) to populate with examples.
- `outputs` -- Component(s) for cached outputs.
- `fn` -- Function to run for caching. Required if `cache_examples=True`.
- `cache_examples` -- Pre-compute outputs. `True` in HF Spaces by default.
- `cache_mode` -- `"eager"` caches at launch, `"lazy"` caches on first use.
- `run_on_click` -- If True, runs `fn` when example is clicked (if not cached).
- `preload` -- Index of example to preload at app start (default 0, set to `False` to disable).

**Usage:**
```python
import gradio as gr

def greet(name, greeting):
    return f"{greeting}, {name}!"

with gr.Blocks() as demo:
    name = gr.Textbox(label="Name")
    greeting = gr.Dropdown(["Hello", "Hi", "Hey"], label="Greeting")
    output = gr.Textbox(label="Output")
    btn = gr.Button("Greet")
    btn.click(greet, [name, greeting], output)

    gr.Examples(
        examples=[["World", "Hello"], ["Gradio", "Hi"]],
        inputs=[name, greeting],
        outputs=output,
        fn=greet,
        cache_examples=True,
    )
demo.launch()
```

---

## Additional APIs

### gr.update()

Dynamically update component properties:
```python
def toggle_visibility(visible):
    return gr.update(visible=not visible)
```

### gr.skip()

Skip updating an output component:
```python
def maybe_update(x):
    if x:
        return x.upper()
    return gr.skip()  # Don't update the output
```

### gr.Info() / gr.Warning() / gr.Error()

Show notifications:
```python
def process(x):
    gr.Info("Processing started")
    if not x:
        gr.Warning("Input is empty")
        raise gr.Error("Cannot process empty input")
    return x
```

### gr.render -- Dynamic Component Rendering

```python
@gr.render(inputs=num_boxes)
def render_boxes(n):
    for i in range(n):
        gr.Textbox(label=f"Box {i}")
```

### gr.set_static_paths()

```python
gr.set_static_paths(["./static/images", "./assets"])
# Files in these dirs are served without copying to temp
```

### gr.Timer

```python
Timer(value: float = 1, *, active: bool = True, render: bool = True)
```

Periodically triggers attached events:
```python
timer = gr.Timer(value=2)  # Every 2 seconds
timer.tick(fn=update_data, inputs=None, outputs=output)
```

### gr.Request

Access HTTP request data in your function:
```python
def greet(name, request: gr.Request):
    return f"Hello {name} from {request.client.host}"
```

---

This documentation was compiled from the installed package source at `/usr/local/lib/python3.11/dist-packages/gradio/` (version 6.5.1 confirmed via `gradio.__version__`).