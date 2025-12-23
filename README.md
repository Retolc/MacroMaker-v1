# MacroMaker

Keyboard and mouse automation macro recorder/player with GUI. Just open a terminal, deploy the dependencies and run the MacroMaker-v1.py

## Features

- Record and replay keyboard/mouse macros
- Visual step-by-step macro editor
- Multiple timing modes (fixed, custom, random)
- Mouse position capture with coordinate preview
- Per-step repetitions
- Global hotkey configuration
- Import/export macros as JSON files
- Real-time execution log

## Installation

### Dependencies
```bash
pip install keyboard pyautogui pillow
```
Note: Requires Python 3.7+ and Windows/Linux with GUI support.

## Usage

### Basic Usage

1. **Run the application:**

   - python "MacroMaker-v1.py"

2. **Create a new macro:**
   - Click "➕ Add Step" to add actions
   - Select action type (keyboard/mouse)
   - Configure timing and repetitions

3. **Save/load macros:**
   - Use "💾 Save" to save current macro
   - Use "📁 Load File" to import JSON macros
   - Macros are stored in `macros.json`

### Macro Actions

#### Keyboard Actions
- Single key presses (e.g., "a", "enter", "space")
- Key combinations (e.g., "Ctrl + C", "Shift + Tab")
- Configure by clicking "Click to set key" and pressing desired keys

#### Mouse Actions
- Move cursor to position
- Left/right/middle click
- Double clicks
- Configure coordinates by clicking "📐" to capture mouse position

### Timing Modes

| Mode | Description | Configuration |
|------|-------------|---------------|
| Fixed | All steps use same delay | Set global delay (default: 0.3s) |
| Custom | Individual delay per step | Set delay for each step |
| Random | Random delay per step | Set min/max range for each step |

### Hotkeys

| Action | Default Hotkey | Configurable |
|--------|----------------|--------------|
| Start macro | Ctrl+Enter | Yes |
| Stop macro | Esc | Yes |
| Capture mouse position | Ctrl+Shift+C | Yes |

Configure hotkeys via "⚙️ Configure Hotkeys" button.

### Step Options

- **Repetitions:** Number of times each step repeats
- **Move steps:** Reorder with ▲/▼ buttons
- **Copy steps:** Create multiple copies of a step
- **Manual edit:** Edit action text directly


## Advanced Configuration

### JSON Macro Format

Example macro structure:
```json
{
  "Test Macro": {
    "nome": "Test Macro",
    "etapas": [
      {
        "tipo": "teclado",
        "acao": "Hello World",
        "tempo": "0.5",
        "repeticoes": 1
      }
    ],
    "repeticoes": 1,
    "modo_tempo": "fixo",
    "tempo_fixo": "0.3"
  }
}
Global Configuration
Edit config_global.json to modify default hotkeys:

json
{
  "hotkey_iniciar": "ctrl+enter",
  "hotkey_parar": "esc",
  "hotkey_captura_mouse": "ctrl+shift+c"
}
```
## Troubleshooting

### Common Issues

1. **Hotkeys not working:**
   - Run as administrator (Windows)
   - Check for conflicting applications
   - Reconfigure hotkeys in settings

2. **Mouse capture not working:**
   - Ensure display is not scaled above 100%
   - Run with administrative privileges

3. **Import errors:**
   - Verify JSON file format
   - Check for syntax errors in macro file

### Dependencies Notes

- **keyboard:** Requires root/admin privileges on Linux
- **pyautogui:** May have issues with multiple displays
- **Pillow:** Required for image processing features

## Development

### Requirements for Development
pip install keyboard pyautogui pillow

text

### Code Structure
- `EditorMacros` class: Main application controller
- GUI built with tkinter
- Threaded macro execution
- JSON-based storage system

## Security Notes

- Application requires input simulation permissions
- Store macros locally only
- No network connectivity or data collection
- Run in trusted environments only

## Compatibility

- **Windows:** 10/11 (fully supported)
- **Linux:** Requires X11/Wayland with GUI
- **macOS:** Not tested (requires modifications)

## License

Free for personal and commercial use. No warranty provided.
