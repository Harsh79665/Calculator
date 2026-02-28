# Modern Tkinter Calculator

A modern, responsive, and visually polished calculator built with **Python** and **Tkinter**.  
It supports both basic and scientific operations, keyboard input, dark/light themes, smooth button animations, and a compact calculation history.

## Features

- **Modern UI**
  - Dark and light themes
  - Soft, flat-styled buttons with hover/pressed animations
  - Clean typography and consistent spacing
  - Small history panel for recent calculations

- **Functionality**
  - Basic operations: `+`, `-`, `*`, `/`, `%`
  - Decimal support
  - Clear (`C`) and Backspace (`⌫`)
  - Sign toggle (`±`) and reciprocal (`1/x`)
  - Scientific mode: `sin`, `cos`, `tan`, `log`, `ln`, `√`, `^`, `π`, `e`, parentheses
  - Error handling for invalid input and divide-by-zero

- **UX Enhancements**
  - Full keyboard input support
  - Smooth button press animation
  - Operator buttons highlighted with accent color
  - Optional sound feedback on button press (on compatible systems)

## Requirements

- Python 3.10+ (Tkinter is included with standard Python on most systems)
- No external packages are required (`requirements.txt` is just informational).

## Running the Application

From the project directory:

```bash
python main.py
```

On some systems you may need:

```bash
python3 main.py
```

## Keyboard Shortcuts

- Digits & decimal: `0-9`, `.`
- Operators: `+`, `-`, `*`, `/`, `%`, `^`, `(`, `)`
- Evaluate: `Enter`
- Clear: `C`, `c`, or `Esc`
- Backspace: `Backspace`

## Notes

- Trigonometric and logarithmic functions use the standard `math` module:
  - Angles are in **radians**.
  - `log` is base-10; `ln` uses natural logarithm.
- The UI is responsive; resize the window to see the layout adapt.

