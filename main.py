import math
import sys
import tkinter as tk
from tkinter import ttk
from typing import Callable, List, Tuple

try:
    import winsound
except ImportError:  # Non-Windows platforms
    winsound = None


class CalculatorLogic:
    """Encapsulates calculator expression handling and evaluation."""

    def __init__(self) -> None:
        self.expression: str = ""
        self.history: list[str] = []

    def clear(self) -> None:
        self.expression = ""

    def backspace(self) -> None:
        if self.expression:
            self.expression = self.expression[:-1]

    def append_token(self, token: str) -> None:
        # Normalized tokens for internal expression
        mapping = {
            "×": "*",
            "÷": "/",
            "^": "**",
            "π": "pi",
            "√": "sqrt(",
        }
        normalized = mapping.get(token, token)
        self.expression += normalized

    def toggle_sign(self) -> None:
        if not self.expression:
            return
        try:
            value = float(self.expression)
            value *= -1
            # Replace entire expression with toggled value
            self.expression = str(value)
        except ValueError:
            # For complex expressions, just prefix or remove leading minus
            if self.expression.startswith("-"):
                self.expression = self.expression[1:]
            else:
                self.expression = "-" + self.expression

    def invert(self) -> None:
        if not self.expression:
            return
        self.expression = f"1/({self.expression})"

    def safe_eval(self) -> str:
        """Safely evaluate the current expression and return a string result."""
        if not self.expression:
            return "0"

        raw_expr = self.expression
        expr = raw_expr.strip()

        # Allowed names from math plus a few builtins
        allowed_names = {
            name: getattr(math, name)
            for name in [
                "sin",
                "cos",
                "tan",
                "sqrt",
                "log",
                "log10",
                "exp",
                "fabs",
                "floor",
                "ceil",
                "factorial",
                "pow",
                "pi",
                "e",
            ]
        }
        allowed_names.update({"abs": abs, "round": round})

        try:
            result = eval(expr, {"__builtins__": {}}, allowed_names)
        except ZeroDivisionError:
            self.expression = ""
            return "Cannot divide by zero"
        except Exception:
            # Reset expression to avoid repeated errors
            self.expression = ""
            return "Invalid expression"

        # Record to history on success
        display_expr = raw_expr
        display_result = str(result)
        self.history.append(f"{display_expr} = {display_result}")
        if len(self.history) > 20:
            self.history.pop(0)

        # Replace expression with result for continued calculations
        self.expression = display_result
        return display_result

    def get_display_value(self) -> str:
        return self.expression if self.expression else "0"


class CalculatorApp:
    """Main Tkinter GUI application for the calculator."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Modern Python Calculator")
        self.root.geometry("420x560")
        self.root.minsize(360, 480)

        self.logic = CalculatorLogic()
        self.display_var = tk.StringVar(value="0")
        self.subdisplay_var = tk.StringVar(value="")
        # Always use light theme; dark mode removed per user request
        self.theme_mode = "light"
        self.sound_enabled = True
        self.scientific_visible = False

        self.style = ttk.Style()
        # Use a base theme that plays well with custom styling
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass

        self._create_theme_palettes()
        self._build_ui()
        self._configure_grid()
        self._apply_theme()
        self._bind_keys()

    def _create_theme_palettes(self) -> None:
        self.themes = {
            "dark": {
                "bg": "#111217",
                "bg_alt": "#181924",
                "button_bg": "#1f2030",
                "button_hover": "#2a2b3d",
                "button_active": "#3a3b4f",
                "button_fg": "#ffffff",
                "operator_bg": "#ff9500",
                "operator_hover": "#ffad33",
                "operator_active": "#e07f00",
                "operator_fg": "#ffffff",
                "accent": "#3d7cff",
                "display_bg": "#111217",
                "display_fg": "#ffffff",
                "subdisplay_fg": "#a0a3b1",
                "border": "#262738",
                "history_bg": "#151624",
                "history_fg": "#d6d7e5",
            },
            "light": {
                "bg": "#f5f5fa",
                "bg_alt": "#ffffff",
                "button_bg": "#f0f1f7",
                "button_hover": "#e0e2f0",
                "button_active": "#d0d3eb",
                "button_fg": "#222222",
                "operator_bg": "#ff9500",
                "operator_hover": "#ffad33",
                "operator_active": "#e07f00",
                "operator_fg": "#ffffff",
                "accent": "#2864ff",
                "display_bg": "#f5f5fa",
                "display_fg": "#111111",
                "subdisplay_fg": "#70738a",
                "border": "#d4d5e0",
                "history_bg": "#f3f3fc",
                "history_fg": "#33354a",
            },
        }

    def _build_ui(self) -> None:
        # Root-level frames
        self.root.configure(bg=self.themes[self.theme_mode]["bg"])

        self.main_container = ttk.Frame(self.root, padding=(16, 16, 16, 16))
        self.main_container.grid(row=0, column=0, sticky="nsew")

        # Top area: display + controls
        self.top_frame = ttk.Frame(self.main_container)
        self.top_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", pady=(0, 12))

        self.subdisplay_label = ttk.Label(
            self.top_frame,
            textvariable=self.subdisplay_var,
            anchor="e",
            font=("Segoe UI", 10),
        )
        self.subdisplay_label.grid(row=0, column=0, columnspan=3, sticky="nsew")

        self.display_entry = ttk.Entry(
            self.top_frame,
            textvariable=self.display_var,
            font=("Segoe UI Semibold", 26),
            justify="right",
            state="readonly",
        )
        self.display_entry.grid(row=1, column=0, columnspan=3, sticky="nsew", pady=(4, 8))

        # Theme and mode toggles
        # theme toggle removed – always light theme
        # self.theme_button = ttk.Button(
        #     self.top_frame,
        #     text="☾ Dark",
        #     command=self.toggle_theme,
        #     width=10,
        # )
        # self.theme_button.grid(row=0, column=3, sticky="e")

        self.mode_button = ttk.Button(
            self.top_frame,
            text="Sci ▾",
            command=self.toggle_scientific,
            width=7,
        )
        self.mode_button.grid(row=1, column=3, sticky="e", padx=(8, 0))

        # Center area: basic buttons
        self.buttons_frame = ttk.Frame(self.main_container)
        self.buttons_frame.grid(row=1, column=0, sticky="nsew")

        # Right area: small history
        self.history_frame = ttk.Frame(self.main_container)
        self.history_frame.grid(row=1, column=1, sticky="nsew", padx=(12, 0))

        history_label = ttk.Label(self.history_frame, text="History", font=("Segoe UI", 10, "bold"))
        history_label.pack(anchor="w")

        self.history_listbox = tk.Listbox(
            self.history_frame,
            height=8,
            borderwidth=0,
            highlightthickness=0,
            activestyle="none",
        )
        self.history_listbox.pack(fill="both", expand=True, pady=(4, 0))

        # Scientific pad (initially hidden)
        self.scientific_frame = ttk.Frame(self.main_container)
        self.scientific_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(10, 0))
        self.scientific_frame.grid_remove()

        # Build button grids
        self._build_basic_buttons()
        self._build_scientific_buttons()

    def _build_basic_buttons(self) -> None:
        # tuple: text, style_key, row, col, handler(token)
        button_specs: List[Tuple[str, str, int, int, Callable[[str], None]]] = [
            ("C", "control", 0, 0, self._handle_clear),
            ("⌫", "control", 0, 1, self._handle_backspace),
            ("%", "operator", 0, 2, self._handle_input),
            ("/", "operator", 0, 3, self._handle_input),
            ("7", "digit", 1, 0, self._handle_input),
            ("8", "digit", 1, 1, self._handle_input),
            ("9", "digit", 1, 2, self._handle_input),
            ("*", "operator", 1, 3, self._handle_input),
            ("4", "digit", 2, 0, self._handle_input),
            ("5", "digit", 2, 1, self._handle_input),
            ("6", "digit", 2, 2, self._handle_input),
            ("-", "operator", 2, 3, self._handle_input),
            ("1", "digit", 3, 0, self._handle_input),
            ("2", "digit", 3, 1, self._handle_input),
            ("3", "digit", 3, 2, self._handle_input),
            ("+", "operator", 3, 3, self._handle_input),
            ("±", "control", 4, 0, self._handle_sign_toggle),
            ("0", "digit", 4, 1, self._handle_input),
            (".", "digit", 4, 2, self._handle_input),
            ("=", "accent", 4, 3, self._handle_equals),
        ]

        self.button_widgets: list[ttk.Button] = []

        for text, style_key, row, col, handler in button_specs:
            btn = self._create_button(
                self.buttons_frame,
                text=text,
                style_key=style_key,
                command=lambda t=text, h=handler: h(t),
            )
            btn.grid(row=row, column=col, sticky="nsew", padx=4, pady=4)
            self.button_widgets.append(btn)

        for r in range(5):
            self.buttons_frame.rowconfigure(r, weight=1, uniform="row")
        for c in range(4):
            self.buttons_frame.columnconfigure(c, weight=1, uniform="col")

    def _build_scientific_buttons(self) -> None:
        sci_specs: List[Tuple[str, int, int]] = [
            ("sin", 0, 0),
            ("cos", 0, 1),
            ("tan", 0, 2),
            ("^", 0, 3),
            ("log", 1, 0),
            ("ln", 1, 1),
            ("√", 1, 2),
            ("(", 1, 3),
            ("π", 2, 0),
            ("e", 2, 1),
            (")", 2, 2),
            ("1/x", 2, 3),
        ]

        self.sci_buttons: list[ttk.Button] = []

        for text, row, col in sci_specs:
            btn = self._create_button(
                self.scientific_frame,
                text=text,
                style_key="sci",
                command=lambda t=text: self._handle_scientific_input(t),
                width=6,
            )
            btn.grid(row=row, column=col, sticky="nsew", padx=4, pady=4)
            self.sci_buttons.append(btn)

        for r in range(3):
            self.scientific_frame.rowconfigure(r, weight=1, uniform="sci_row")
        for c in range(4):
            self.scientific_frame.columnconfigure(c, weight=1, uniform="sci_col")

    def _configure_grid(self) -> None:
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        self.main_container.rowconfigure(0, weight=0)
        self.main_container.rowconfigure(1, weight=1)
        self.main_container.rowconfigure(2, weight=0)
        self.main_container.columnconfigure(0, weight=3)
        self.main_container.columnconfigure(1, weight=2)

        self.top_frame.columnconfigure(0, weight=1)
        self.top_frame.columnconfigure(1, weight=1)
        self.top_frame.columnconfigure(2, weight=1)
        self.top_frame.columnconfigure(3, weight=0)

    def _create_button(
        self,
        parent: tk.Widget,
        text: str,
        style_key: str,
        command: Callable[[], None],
        width: int | None = None,
    ) -> ttk.Button:
        style_name = self._style_name_for_key(style_key)
        btn = ttk.Button(parent, text=text, style=style_name, command=lambda: self._on_button_press(command))

        # Ensure consistent padding to emulate soft rounded buttons
        if width is not None:
            btn.configure(width=width)

        return btn

    def _style_name_for_key(self, key: str) -> str:
        return {
            "digit": "Digit.TButton",
            "operator": "Operator.TButton",
            "control": "Control.TButton",
            "accent": "Accent.TButton",
            "sci": "Sci.TButton",
        }[key]

    def _apply_theme(self) -> None:
        theme = self.themes[self.theme_mode]

        self.root.configure(bg=theme["bg"])
        self.main_container.configure(style="Container.TFrame")
        self.top_frame.configure(style="Container.TFrame")
        self.buttons_frame.configure(style="Container.TFrame")
        self.history_frame.configure(style="Container.TFrame")
        self.scientific_frame.configure(style="Container.TFrame")

        self.style.configure(
            "Container.TFrame",
            background=theme["bg"],
        )
        self.style.configure(
            "TLabel",
            background=theme["bg"],
            foreground=theme["display_fg"],
        )
        self.style.configure(
            "Sub.TLabel",
            background=theme["bg"],
            foreground=theme["subdisplay_fg"],
        )

        self.subdisplay_label.configure(style="Sub.TLabel")

        # Display styling
        self.display_entry.configure(
            foreground=theme["display_fg"],
            justify="right",
        )
        # ttk.Entry uses standard background options via style map; apply via option database
        # tkinter stubs are imprecise, ignore type issues for option_add
        self.root.option_add("*TEntry*background", theme["display_bg"])  # type: ignore
        self.root.option_add("*TEntry*fieldbackground", theme["display_bg"])  # type: ignore

        # History styling
        self.history_listbox.configure(
            bg=theme["history_bg"],
            fg=theme["history_fg"],
            selectbackground=theme["accent"],
            selectforeground=theme["button_fg"],
        )

        # Button styles with hover and active states
        self._configure_button_style(
            "Digit.TButton",
            fg=theme["button_fg"],
            bg=theme["button_bg"],
            hover_bg=theme["button_hover"],
            active_bg=theme["button_active"],
        )
        self._configure_button_style(
            "Control.TButton",
            fg=theme["button_fg"],
            bg=theme["bg_alt"],
            hover_bg=theme["button_hover"],
            active_bg=theme["button_active"],
        )
        self._configure_button_style(
            "Sci.TButton",
            fg=theme["button_fg"],
            bg=theme["bg_alt"],
            hover_bg=theme["button_hover"],
            active_bg=theme["button_active"],
        )
        self._configure_button_style(
            "Operator.TButton",
            fg=theme["operator_fg"],
            bg=theme["operator_bg"],
            hover_bg=theme["operator_hover"],
            active_bg=theme["operator_active"],
        )
        self._configure_button_style(
            "Accent.TButton",
            fg=theme["button_fg"],
            bg=theme["accent"],
            hover_bg=theme["operator_hover"],
            active_bg=theme["operator_active"],
        )

        # Toggle button styling
        self._configure_button_style(
            "TButton",
            fg=theme["button_fg"],
            bg=theme["bg_alt"],
            hover_bg=theme["button_hover"],
            active_bg=theme["button_active"],
        )

    def _configure_button_style(
        self,
        style_name: str,
        fg: str,
        bg: str,
        hover_bg: str,
        active_bg: str,
    ) -> None:
        self.style.configure(
            style_name,
            background=bg,
            foreground=fg,
            borderwidth=0,
            focusthickness=0,
            padding=(10, 8),
            relief="flat",
        )
        self.style.map(
            style_name,
            background=[
                ("pressed", active_bg),
                ("active", hover_bg),
            ],
            relief=[
                ("pressed", "sunken"),
                ("!pressed", "flat"),
            ],
        )

    def _bind_keys(self) -> None:
        self.root.bind("<Key>", self._on_key_press)

    def _on_button_press(self, handler: Callable[[], None]) -> None:
        self._play_click_sound()
        handler()

    def _play_click_sound(self) -> None:
        if not self.sound_enabled or winsound is None:
            return
        try:
            winsound.MessageBeep(winsound.MB_OK)
        except Exception:
            # Fallback to default beep if specific sound fails
            try:
                winsound.MessageBeep()
            except Exception:
                pass

    def _handle_input(self, token: str) -> None:
        if self.display_var.get() in ("Invalid expression", "Cannot divide by zero"):
            self.logic.clear()
        self.logic.append_token(token)
        self.display_var.set(self.logic.get_display_value())

    def _handle_scientific_input(self, token: str) -> None:
        if token == "1/x":
            self.logic.invert()
        elif token == "ln":
            self.logic.append_token("log(")
        else:
            self.logic.append_token(token)
        self.display_var.set(self.logic.get_display_value())

    def _handle_clear(self, _token: str | None = None) -> None:
        self.logic.clear()
        self.subdisplay_var.set("")
        self.display_var.set("0")

    def _handle_backspace(self, _token: str | None = None) -> None:
        if self.display_var.get() in ("Invalid expression", "Cannot divide by zero"):
            self._handle_clear(None)
            return
        self.logic.backspace()
        self.display_var.set(self.logic.get_display_value())

    def _handle_equals(self, _token: str | None = None) -> None:
        expr_before = self.logic.get_display_value()
        result = self.logic.safe_eval()
        self.subdisplay_var.set(expr_before)
        self.display_var.set(result)
        self._refresh_history()

    def _handle_sign_toggle(self, _token: str | None = None) -> None:
        if self.display_var.get() in ("Invalid expression", "Cannot divide by zero"):
            return
        self.logic.toggle_sign()
        self.display_var.set(self.logic.get_display_value())

    def _refresh_history(self) -> None:
        self.history_listbox.delete(0, tk.END)
        for item in reversed(self.logic.history[-8:]):
            self.history_listbox.insert(tk.END, item)

    def toggle_theme(self) -> None:
        # removed; theme is permanently light
        pass

    def toggle_scientific(self) -> None:
        self.scientific_visible = not self.scientific_visible
        if self.scientific_visible:
            self.scientific_frame.grid()
            self.mode_button.configure(text="Sci ▴")
        else:
            self.scientific_frame.grid_remove()
            self.mode_button.configure(text="Sci ▾")

    def _on_key_press(self, event: tk.Event) -> None:
        char = event.char
        keysym = event.keysym

        if char in "0123456789.+-*/%()^":
            self._on_button_press(lambda: self._handle_input(char))
        elif keysym in ("Return", "KP_Enter"):
            self._on_button_press(lambda: self._handle_equals(None))
        elif keysym == "BackSpace":
            self._on_button_press(lambda: self._handle_backspace(None))
        elif keysym == "Escape":
            self._on_button_press(lambda: self._handle_clear(None))
        elif char in ("c", "C"):
            self._on_button_press(lambda: self._handle_clear(None))

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    try:
        root = tk.Tk()
    except tk.TclError as exc:
        print("Failed to initialize Tkinter GUI:", exc, file=sys.stderr)
        raise SystemExit(1)

    app = CalculatorApp(root)
    app.run()


if __name__ == "__main__":
    main()

