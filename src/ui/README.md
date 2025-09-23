# MCP Memory Server UI

This directory contains the UI components for the MCP Memory Server. The UI is built using PySide6 (Qt for Python) and provides a graphical interface for interacting with the memory server.

## Structure

- `main.py`: Main entry point for the UI
- `main_window.py`: Main window implementation
- `memory_adapter.py`: Direct adapter to the memory manager
- `widgets/`: UI widget components
  - `memory_browser.py`: Widget for browsing and searching memory

## Dependencies

- PySide6: Qt bindings for Python
- Other dependencies from the MCP project

## Usage

The UI can be launched in two ways:

1. Automatically when the memory server starts (with the `--launch-ui` flag)
2. Manually by running `python -m src.ui.main`

## Development

This is the initial implementation with placeholder components. The UI will be developed incrementally in the following steps:

1. Basic structure and dependencies (current step)
2. Memory adapter implementation
3. Memory browser widget implementation
4. Full integration with the memory server

## Status

This is a work in progress. The current implementation includes only placeholder components.