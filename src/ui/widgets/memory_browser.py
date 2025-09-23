"""
MCP Memory Server UI - Memory Browser Widget
Widget for browsing and searching the MCP memory database.
"""

import logging
import asyncio
from typing import Optional, List, Dict, Any
import os
import json
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QGroupBox,
    QTextEdit,
    QHeaderView,
    QSplitter,
    QApplication,
    QMessageBox,
    QTabWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QFileDialog,
    QProgressBar,
    QCheckBox,
    QFrame,
)
from PySide6.QtCore import Signal, Qt, Slot, QTimer
from PySide6.QtGui import QFont

from src.ui.memory_adapter import MemoryAdapter


logger = logging.getLogger(__name__)


class MemoryBrowserWidget(QWidget):
    """Widget for browsing and searching memory."""
    
    memory_selected = Signal(dict)
    
    def __init__(self, memory_adapter: Optional[MemoryAdapter] = None):
        """Initialize the memory browser widget.
        
        Args:
            memory_adapter: Optional memory adapter for direct access.
        """
        super().__init__()
        self.memory_adapter = memory_adapter
        self.current_results = []
        self.collections = ["global_memory", "learned_memory", "agent_memory"]
        self.selected_memory = None
        self.is_initialized = False
        self.stats_refresh_timer = None
        
        # Create UI
        self.setup_ui()
    
    def setup_ui(self) -> None:
        """Set up the UI components."""
        # Main layout
        layout = QVBoxLayout(self)
        
        # Status bar for memory connection
        self.setup_status_bar(layout)
        
        # Main content with tabs
        self.setup_main_content(layout)
    
    def setup_status_bar(self, layout) -> None:
        """Set up memory connection status bar."""
        status_frame = QFrame()
        status_frame.setFrameStyle(QFrame.StyledPanel)
        status_frame.setMaximumHeight(35)
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(5, 2, 5, 2)
        
        self.status_label = QLabel("Memory: Connecting...")
        self.status_label.setStyleSheet(
            "QLabel { color: orange; font-weight: bold; padding: 4px; }"
        )
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        layout.addWidget(status_frame)
    
    def setup_main_content(self, layout) -> None:
        """Set up main tabbed content area."""
        self.tab_widget = QTabWidget()
        
        # Results tab
        self.setup_results_tab()
        
        # Upload tab
        self.setup_upload_tab()
        
        # Statistics tab
        self.setup_statistics_tab()
        
        # Collections tab
        self.setup_collections_tab()
        
        layout.addWidget(self.tab_widget)
    
    def setup_results_tab(self) -> None:
        """Set up search results tab."""
        results_widget = QWidget()
        results_layout = QVBoxLayout(results_widget)
        
        # Search controls group
        search_group = QGroupBox("Search Memory")
        search_layout = QVBoxLayout(search_group)
        
        # Search options row
        options_row = QHBoxLayout()
        
        # Collection selector
        options_row.addWidget(QLabel("Collection:"))
        self.collection_combo = QComboBox()
        self.collection_combo.addItems(self.collections)
        options_row.addWidget(self.collection_combo)
        
        # Limit selector
        options_row.addWidget(QLabel("Limit:"))
        self.limit_spin = QSpinBox()
        self.limit_spin.setRange(1, 100)
        self.limit_spin.setValue(10)
        options_row.addWidget(self.limit_spin)
        
        # Auto-search checkbox
        self.auto_search_cb = QCheckBox("Auto Search")
        self.auto_search_cb.setChecked(False)
        options_row.addWidget(self.auto_search_cb)
        
        options_row.addStretch()
        search_layout.addLayout(options_row)
        
        # Search input row
        search_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter search query...")
        self.search_input.returnPressed.connect(self.on_search_clicked)
        self.search_input.textChanged.connect(self.on_search_text_changed)
        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self.on_search_clicked)
        search_row.addWidget(self.search_input)
        search_row.addWidget(self.search_btn)
        search_layout.addLayout(search_row)
        
        results_layout.addWidget(search_group)
        
        # Results header
        header_layout = QHBoxLayout()
        self.results_label = QLabel("No search performed")
        header_layout.addWidget(self.results_label)
        header_layout.addStretch()
        
        self.clear_btn = QPushButton("Clear Results")
        self.clear_btn.clicked.connect(self.on_clear_results)
        header_layout.addWidget(self.clear_btn)
        
        results_layout.addLayout(header_layout)
        
        # Create splitter for results and details
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Results table
        results_table_widget = QWidget()
        results_table_layout = QVBoxLayout(results_table_widget)
        
        self.results_table = QTableWidget(0, 4)
        self.results_table.setHorizontalHeaderLabels(
            ["Score", "Collection", "Content", "ID"]
        )
        self.results_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.results_table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )
        self.results_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.results_table.setAlternatingRowColors(True)
        self.results_table.horizontalHeader().setStretchLastSection(True)
        self.results_table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch
        )
        self.results_table.setColumnWidth(0, 80)  # Score
        self.results_table.setColumnWidth(1, 120)  # Collection
        self.results_table.setColumnWidth(3, 120)  # ID
        
        self.results_table.itemSelectionChanged.connect(
            self.on_result_selected
        )
        
        results_table_layout.addWidget(self.results_table)
        splitter.addWidget(results_table_widget)
        
        # Details section
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        
        detail_group = QGroupBox("Memory Details")
        detail_inner_layout = QVBoxLayout(detail_group)
        
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        detail_inner_layout.addWidget(self.detail_text)
        
        # Action buttons
        action_row = QHBoxLayout()
        action_row.addStretch()
        
        self.delete_btn = QPushButton("Delete Memory")
        self.delete_btn.setEnabled(False)
        self.delete_btn.clicked.connect(self.on_delete_clicked)
        action_row.addWidget(self.delete_btn)
        
        detail_inner_layout.addLayout(action_row)
        details_layout.addWidget(detail_group)
        splitter.addWidget(details_widget)
        
        # Set initial sizes
        splitter.setSizes([400, 200])
        
        results_layout.addWidget(splitter)
        
        self.tab_widget.addTab(results_widget, "Search Results")
    
    def setup_upload_tab(self) -> None:
        """Set up file upload tab."""
        upload_widget = QWidget()
        upload_layout = QVBoxLayout(upload_widget)
        
        # Upload instructions
        instructions_group = QGroupBox("File Upload Instructions")
        instructions_layout = QVBoxLayout(instructions_group)
        
        instructions_text = QTextEdit()
        instructions_text.setReadOnly(True)
        instructions_text.setMaximumHeight(100)
        instructions_text.setHtml(
            "<p>Upload text files to add them to memory:</p>"
            "<ol>"
            "<li>Select a collection</li>"
            "<li>Choose files to upload</li>"
            "<li>Click 'Upload Files'</li>"
            "</ol>"
            "<p>Supported formats: .txt, .md, .json</p>"
        )
        instructions_layout.addWidget(instructions_text)
        upload_layout.addWidget(instructions_group)
        
        # Upload form
        form_group = QGroupBox("Upload Form")
        form_layout = QVBoxLayout(form_group)
        
        # Collection selection
        collection_row = QHBoxLayout()
        collection_row.addWidget(QLabel("Collection:"))
        self.upload_collection_combo = QComboBox()
        self.upload_collection_combo.addItems(self.collections)
        collection_row.addWidget(self.upload_collection_combo)
        collection_row.addStretch()
        form_layout.addLayout(collection_row)
        
        # File selection
        file_row = QHBoxLayout()
        self.file_path_input = QLineEdit()
        self.file_path_input.setReadOnly(True)
        self.file_path_input.setPlaceholderText("Select files to upload...")
        file_row.addWidget(self.file_path_input)
        
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self.on_browse_files)
        file_row.addWidget(self.browse_btn)
        form_layout.addLayout(file_row)
        
        # Upload button
        upload_row = QHBoxLayout()
        upload_row.addStretch()
        self.upload_btn = QPushButton("Upload Files")
        self.upload_btn.clicked.connect(self.on_upload_clicked)
        upload_row.addWidget(self.upload_btn)
        form_layout.addLayout(upload_row)
        
        # Progress bar
        self.upload_progress = QProgressBar()
        self.upload_progress.setVisible(False)
        form_layout.addWidget(self.upload_progress)
        
        # Upload status
        self.upload_status = QTextEdit()
        self.upload_status.setReadOnly(True)
        self.upload_status.setMaximumHeight(150)
        form_layout.addWidget(self.upload_status)
        
        upload_layout.addWidget(form_group)
        upload_layout.addStretch()
        
        self.tab_widget.addTab(upload_widget, "Upload Files")
    
    def setup_statistics_tab(self) -> None:
        """Set up memory statistics tab."""
        stats_widget = QWidget()
        stats_layout = QVBoxLayout(stats_widget)
        
        # Statistics display
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setFont(QFont("monospace"))
        stats_layout.addWidget(self.stats_text)
        
        # Refresh button
        button_row = QHBoxLayout()
        button_row.addStretch()
        self.refresh_stats_btn = QPushButton("Refresh Statistics")
        self.refresh_stats_btn.clicked.connect(self.on_refresh_stats_clicked)
        button_row.addWidget(self.refresh_stats_btn)
        stats_layout.addLayout(button_row)
        
        self.tab_widget.addTab(stats_widget, "Statistics")
    
    def setup_collections_tab(self) -> None:
        """Set up collections management tab."""
        collections_widget = QWidget()
        collections_layout = QVBoxLayout(collections_widget)
        
        # Collections tree
        self.collections_tree = QTreeWidget()
        self.collections_tree.setHeaderLabels(
            ["Collection", "Documents", "Vectors", "Status"]
        )
        collections_layout.addWidget(self.collections_tree)
        
        # Collection actions
        actions_row = QHBoxLayout()
        actions_row.addStretch()
        
        self.refresh_collections_btn = QPushButton("Refresh")
        self.refresh_collections_btn.clicked.connect(self.on_refresh_collections_clicked)
        actions_row.addWidget(self.refresh_collections_btn)
        
        self.delete_collection_btn = QPushButton("Delete Collection")
        self.delete_collection_btn.clicked.connect(self.on_delete_collection_clicked)
        actions_row.addWidget(self.delete_collection_btn)
        
        collections_layout.addLayout(actions_row)
        
        self.tab_widget.addTab(collections_widget, "Collections")
    
    def initialize(self) -> None:
        """Initialize the widget with the memory adapter."""
        if self.is_initialized or not self.memory_adapter:
            return
        
        # Start a task to load collections
        self.load_collections()
        
        # Initialize stats refresh timer
        self.stats_refresh_timer = QTimer(self)
        self.stats_refresh_timer.timeout.connect(self.refresh_stats)
        self.stats_refresh_timer.start(30000)  # Update every 30 seconds
        
        # Initial data load
        self.refresh_data()
        
        self.is_initialized = True
    
    def refresh_data(self) -> None:
        """Refresh all data displays."""
        # Load collections
        self.load_collections()
        
        # Load stats
        self.refresh_stats()
        
        # Load collections data
        self.refresh_collections()
    
    async def _do_load_collections(self) -> None:
        """Asynchronously load collections from the memory adapter."""
        try:
            if not self.memory_adapter:
                return
            
            collections = await self.memory_adapter.get_collections()
            if collections:
                self.collections = collections
                
                # Update collection combos
                self.collection_combo.clear()
                self.collection_combo.addItems(self.collections)
                
                self.upload_collection_combo.clear()
                self.upload_collection_combo.addItems(self.collections)
                
                # Update status
                self.status_label.setText(
                    f"Loaded {len(collections)} collections"
                )
                self.status_label.setStyleSheet(
                    "QLabel { color: green; font-weight: bold; padding: 4px; }"
                )
        except Exception as e:
            logger.error(f"Error loading collections: {e}")
            self.status_label.setText(f"Error loading collections: {str(e)}")
            self.status_label.setStyleSheet(
                "QLabel { color: red; font-weight: bold; padding: 4px; }"
            )
    
    def load_collections(self) -> None:
        """Load collections from the memory adapter."""
        asyncio.create_task(self._do_load_collections())
    
    @Slot()
    def on_search_text_changed(self) -> None:
        """Handle search text changes for auto-search."""
        if self.auto_search_cb.isChecked():
            # Debounce auto-search
            if hasattr(self, "auto_search_timer"):
                self.auto_search_timer.stop()
            
            # Create timer if not exists
            if not hasattr(self, "auto_search_timer"):
                self.auto_search_timer = QTimer(self)
                self.auto_search_timer.setSingleShot(True)
                self.auto_search_timer.timeout.connect(self.on_search_clicked)
            
            # Start timer
            self.auto_search_timer.start(500)  # 500ms debounce
    
    @Slot()
    def on_search_clicked(self) -> None:
        """Handle search button click."""
        query = self.search_input.text().strip()
        if not query:
            QMessageBox.warning(
                self, "Empty Query", "Please enter a search query."
            )
            return
        
        collection = self.collection_combo.currentText()
        limit = self.limit_spin.value()
        
        # Clear results
        self.results_table.setRowCount(0)
        self.current_results = []
        self.detail_text.clear()
        self.delete_btn.setEnabled(False)
        self.selected_memory = None
        
        # Set status
        self.results_label.setText(
            f"Searching '{collection}' for '{query}'..."
        )
        
        # Start search task
        asyncio.create_task(
            self._do_search(query, collection, limit)
        )
    
    @Slot()
    def on_clear_results(self) -> None:
        """Clear search results."""
        self.results_table.setRowCount(0)
        self.current_results = []
        self.detail_text.clear()
        self.delete_btn.setEnabled(False)
        self.selected_memory = None
        self.results_label.setText("Results cleared")
    
    async def _do_search(
        self, query: str, collection: str, limit: int
    ) -> None:
        """Asynchronously perform search using memory adapter."""
        try:
            if not self.memory_adapter:
                self.status_label.setText("Memory adapter not initialized")
                self.status_label.setStyleSheet(
                    "QLabel { color: red; font-weight: bold; padding: 4px; }"
                )
                return
            
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            
            results = await self.memory_adapter.search_memory(
                query, collection, limit
            )
            
            self.current_results = results
            self._display_results()
            
            self.results_label.setText(
                f"Found {len(results)} results for '{query}'"
            )
        except Exception as e:
            logger.error(f"Search error: {e}")
            self.results_label.setText(f"Search error: {str(e)}")
        finally:
            QApplication.restoreOverrideCursor()
    
    def _display_results(self) -> None:
        """Display search results in the table."""
        self.results_table.setRowCount(0)
        
        if not self.current_results:
            return
        
        self.results_table.setRowCount(len(self.current_results))
        
        for row, result in enumerate(self.current_results):
            score = result.get("score", 0.0)
            payload = result.get("payload", {})
            content = payload.get("content", "")
            collection = payload.get("collection", "unknown")
            memory_id = result.get("id", "unknown")
            
            # Truncate content for display
            display_content = content
            if len(display_content) > 100:
                display_content = display_content[:97] + "..."
            
            # Set items
            self.results_table.setItem(
                row, 0, QTableWidgetItem(f"{score:.4f}")
            )
            self.results_table.setItem(
                row, 1, QTableWidgetItem(collection)
            )
            self.results_table.setItem(
                row, 2, QTableWidgetItem(display_content)
            )
            self.results_table.setItem(
                row, 3, QTableWidgetItem(memory_id)
            )
        
        # Auto-resize columns to content
        self.results_table.resizeColumnsToContents()
        # But ensure content column still gets stretched
        self.results_table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch
        )
    
    @Slot()
    def on_result_selected(self) -> None:
        """Handle result selection."""
        selected_rows = self.results_table.selectionModel().selectedRows()
        if not selected_rows:
            self.detail_text.clear()
            self.delete_btn.setEnabled(False)
            self.selected_memory = None
            return
        
        row = selected_rows[0].row()
        if row < 0 or row >= len(self.current_results):
            return
        
        memory = self.current_results[row]
        self.selected_memory = memory
        
        # Display details
        payload = memory.get("payload", {})
        content = payload.get("content", "")
        collection = payload.get("collection", "unknown")
        memory_type = payload.get("memory_type", "unknown")
        timestamp = payload.get("timestamp", "")
        memory_id = memory.get("id", "unknown")
        score = memory.get("score", 0.0)
        
        details = (
            f"<h3>Memory Details</h3>"
            f"<p><b>ID:</b> {memory_id}</p>"
            f"<p><b>Collection:</b> {collection}</p>"
            f"<p><b>Memory Type:</b> {memory_type}</p>"
            f"<p><b>Score:</b> {score:.4f}</p>"
            f"<p><b>Timestamp:</b> {timestamp}</p>"
            f"<h4>Content:</h4>"
            f"<pre>{content}</pre>"
        )
        
        self.detail_text.setHtml(details)
        self.delete_btn.setEnabled(True)
        
        # Emit signal
        self.memory_selected.emit(memory)
    
    @Slot()
    def on_delete_clicked(self) -> None:
        """Handle delete button click."""
        if not self.selected_memory:
            return
        
        memory_id = self.selected_memory.get("id", "")
        payload = self.selected_memory.get("payload", {})
        collection = payload.get("collection", "")
        
        if not memory_id or not collection:
            QMessageBox.warning(
                self, "Delete Error", 
                "Cannot delete memory: missing ID or collection."
            )
            return
        
        # Confirm deletion
        confirm = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to delete memory {memory_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            # Start delete task
            asyncio.create_task(
                self._do_delete(collection, memory_id)
            )
    
    async def _do_delete(self, collection: str, memory_id: str) -> None:
        """Asynchronously delete memory point."""
        try:
            if not self.memory_adapter:
                self.status_label.setText("Memory adapter not initialized")
                self.status_label.setStyleSheet(
                    "QLabel { color: red; font-weight: bold; padding: 4px; }"
                )
                return
            
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            
            success = await self.memory_adapter.delete_memory_point(
                collection, memory_id
            )
            
            if success:
                self.status_label.setText(
                    f"Deleted memory {memory_id} from {collection}"
                )
                self.status_label.setStyleSheet(
                    "QLabel { color: green; font-weight: bold; padding: 4px; }"
                )
                
                # Remove from results
                self.current_results = [
                    r for r in self.current_results
                    if r.get("id") != memory_id
                ]
                self._display_results()
                
                # Clear details
                self.detail_text.clear()
                self.delete_btn.setEnabled(False)
                self.selected_memory = None
                
                # Refresh stats and collections
                self.refresh_stats()
                self.refresh_collections()
            else:
                self.status_label.setText(
                    f"Failed to delete memory {memory_id}"
                )
                self.status_label.setStyleSheet(
                    "QLabel { color: red; font-weight: bold; padding: 4px; }"
                )
                QMessageBox.warning(
                    self, "Delete Failed",
                    f"Failed to delete memory {memory_id}."
                )
        except Exception as e:
            logger.error(f"Delete error: {e}")
            self.status_label.setText(f"Delete error: {str(e)}")
            self.status_label.setStyleSheet(
                "QLabel { color: red; font-weight: bold; padding: 4px; }"
            )
            QMessageBox.critical(
                self, "Delete Error",
                f"Error deleting memory: {str(e)}"
            )
        finally:
            QApplication.restoreOverrideCursor()
    
    @Slot()
    def on_browse_files(self) -> None:
        """Browse for files to upload."""
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilter("Text Files (*.txt *.md *.json)")
        
        if file_dialog.exec():
            file_paths = file_dialog.selectedFiles()
            self.file_path_input.setText(", ".join(file_paths))
    
    @Slot()
    def on_upload_clicked(self) -> None:
        """Handle upload button click."""
        file_paths_text = self.file_path_input.text()
        if not file_paths_text:
            QMessageBox.warning(
                self, "No Files Selected", 
                "Please select files to upload."
            )
            return
        
        file_paths = [p.strip() for p in file_paths_text.split(",")]
        collection = self.upload_collection_combo.currentText()
        
        # Validate files
        valid_files = []
        for path in file_paths:
            if not os.path.exists(path):
                self.upload_status.append(f"❌ File not found: {path}")
                continue
            
            if not os.path.isfile(path):
                self.upload_status.append(f"❌ Not a file: {path}")
                continue
            
            _, ext = os.path.splitext(path)
            if ext.lower() not in [".txt", ".md", ".json"]:
                self.upload_status.append(
                    f"❌ Unsupported file type: {path}"
                )
                continue
            
            valid_files.append(path)
        
        if not valid_files:
            QMessageBox.warning(
                self, "No Valid Files", 
                "None of the selected files are valid for upload."
            )
            return
        
        # Clear status and show progress
        self.upload_status.clear()
        self.upload_status.append(
            f"Starting upload of {len(valid_files)} files to {collection}..."
        )
        
        self.upload_progress.setVisible(True)
        self.upload_progress.setRange(0, len(valid_files))
        self.upload_progress.setValue(0)
        
        self.upload_btn.setEnabled(False)
        
        # Start upload task
        asyncio.create_task(
            self._do_upload(valid_files, collection)
        )
    
    async def _do_upload(self, file_paths: List[str], collection: str) -> None:
        """Asynchronously upload files to memory."""
        try:
            if not self.memory_adapter:
                self.upload_status.append("❌ Memory adapter not initialized")
                self.upload_btn.setEnabled(True)
                self.upload_progress.setVisible(False)
                return
            
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            
            successful = 0
            failed = 0
            
            for i, path in enumerate(file_paths):
                try:
                    # Read file content
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    # Prepare metadata
                    filename = os.path.basename(path)
                    file_ext = os.path.splitext(filename)[1].lower()
                    
                    metadata = {
                        "source": "ui_upload",
                        "filename": filename,
                        "file_type": file_ext.lstrip("."),
                        "upload_time": datetime.now().isoformat()
                    }
                    
                    # Upload to memory through adapter
                    success = await self.memory_adapter.upload_document(
                        collection=collection,
                        content=content,
                        metadata=metadata
                    )
                    
                    # Update progress
                    self.upload_progress.setValue(i + 1)
                    
                    if success:
                        self.upload_status.append(
                            f"✅ Uploaded: {os.path.basename(path)}"
                        )
                        successful += 1
                    else:
                        self.upload_status.append(
                            f"❌ Failed to upload {path}: Upload returned false"
                        )
                        failed += 1
                except Exception as e:
                    self.upload_status.append(
                        f"❌ Failed to upload {path}: {str(e)}"
                    )
                    failed += 1
            
            self.upload_status.append(
                f"Upload complete. {successful} of {len(file_paths)} "
                f"files uploaded successfully. {failed} failed."
            )
            
            # Refresh stats and collections
            self.refresh_stats()
            self.refresh_collections()
            
        except Exception as e:
            logger.error(f"Upload error: {e}")
            self.upload_status.append(f"❌ Upload error: {str(e)}")
        finally:
            self.upload_btn.setEnabled(True)
            self.upload_progress.setVisible(False)
            QApplication.restoreOverrideCursor()
    
    @Slot()
    def on_refresh_stats_clicked(self) -> None:
        """Handle refresh stats button click."""
        self.refresh_stats()
    
    def refresh_stats(self) -> None:
        """Refresh memory statistics."""
        asyncio.create_task(self._do_refresh_stats())
    
    async def _do_refresh_stats(self) -> None:
        """Asynchronously refresh memory statistics."""
        try:
            if not self.memory_adapter:
                self.stats_text.setPlainText("Memory adapter not initialized")
                return
            
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            
            stats = await self.memory_adapter.get_stats()
            
            # Format statistics
            stats_text = "Memory Statistics\n"
            stats_text += "=" * 50 + "\n\n"
            
            # Overall status
            stats_text += f"Status: {stats.get('status', 'unknown')}\n"
            stats_text += f"Total Collections: {stats.get('total_collections', 0)}\n"
            stats_text += f"Collections Ready: {stats.get('collections_ready', 0)}\n"
            stats_text += f"Total Documents: {stats.get('total_documents', 0)}\n"
            
            if stats.get('message'):
                stats_text += f"Message: {stats.get('message')}\n"
            
            stats_text += "\nCollection Details:\n"
            stats_text += "-" * 50 + "\n"
            
            # Collection details - filter out the known keys
            known_keys = {
                "status", "total_collections", "collections_ready", 
                "total_documents", "message", "collections"
            }
            
            for key, value in stats.items():
                if key not in known_keys and isinstance(value, dict):
                    # This is likely a collection
                    stats_text += f"\n{key}:\n"
                    for stat_key, stat_value in value.items():
                        stats_text += f"  {stat_key}: {stat_value}\n"
            
            self.stats_text.setPlainText(stats_text)
            
        except Exception as e:
            logger.error(f"Error refreshing stats: {e}")
            self.stats_text.setPlainText(f"Error refreshing stats: {str(e)}")
        finally:
            QApplication.restoreOverrideCursor()
    
    @Slot()
    def on_refresh_collections_clicked(self) -> None:
        """Handle refresh collections button click."""
        self.refresh_collections()
    
    def refresh_collections(self) -> None:
        """Refresh collections display."""
        asyncio.create_task(self._do_refresh_collections())
    
    async def _do_refresh_collections(self) -> None:
        """Asynchronously refresh collections display."""
        try:
            if not self.memory_adapter:
                return
            
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            
            # Get collections
            collections = await self.memory_adapter.get_collections()
            
            # Get stats for additional details
            stats = await self.memory_adapter.get_stats()
            
            # Clear tree
            self.collections_tree.clear()
            
            # Populate tree
            for collection in collections:
                # Create tree item
                item = QTreeWidgetItem([collection, "0", "0", "unknown"])
                
                # Try to get details from stats
                if collection in stats:
                    col_stats = stats[collection]
                    documents = col_stats.get("documents_count", 0)
                    vectors = col_stats.get("vectors_count", 0)
                    status = col_stats.get("status", "unknown")
                    
                    item.setText(1, str(documents))
                    item.setText(2, str(vectors))
                    item.setText(3, status)
                    
                    # Set color based on status
                    if status == "green":
                        for col in range(4):
                            item.setForeground(col, Qt.GlobalColor.darkGreen)
                    elif status == "yellow":
                        for col in range(4):
                            item.setForeground(col, Qt.GlobalColor.darkYellow)
                    elif status == "red":
                        for col in range(4):
                            item.setForeground(col, Qt.GlobalColor.darkRed)
                
                self.collections_tree.addTopLevelItem(item)
            
            # Resize columns to content
            for col in range(4):
                self.collections_tree.resizeColumnToContents(col)
            
        except Exception as e:
            logger.error(f"Error refreshing collections: {e}")
        finally:
            QApplication.restoreOverrideCursor()
    
    @Slot()
    def on_delete_collection_clicked(self) -> None:
        """Handle delete collection button click."""
        selected_item = self.collections_tree.currentItem()
        if not selected_item:
            QMessageBox.warning(
                self, "No Collection Selected",
                "Please select a collection to delete."
            )
            return
        
        collection = selected_item.text(0)
        
        # Confirm deletion
        confirm = QMessageBox.question(
            self, "Confirm Collection Deletion",
            f"Are you sure you want to delete the entire '{collection}' collection?\n\n"
            "This will permanently delete all memory points in this collection "
            "and cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            # Start delete task
            asyncio.create_task(self._do_delete_collection(collection))
    
    async def _do_delete_collection(self, collection: str) -> None:
        """Asynchronously delete a collection."""
        try:
            if not self.memory_adapter:
                QMessageBox.warning(
                    self, "Not Connected",
                    "Memory adapter is not initialized."
                )
                return
            
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            
            success = await self.memory_adapter.delete_collection(collection)
            
            if success:
                QMessageBox.information(
                    self, "Collection Deleted",
                    f"The collection '{collection}' was successfully deleted."
                )
                # Refresh to show it's gone
                self.refresh_collections()
                self.refresh_stats()
            else:
                QMessageBox.critical(
                    self, "Deletion Failed",
                    f"Failed to delete collection '{collection}'. "
                    "See logs for details."
                )
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")
            QMessageBox.critical(
                self, "Error",
                f"An error occurred while deleting the collection: {str(e)}"
            )
        finally:
            QApplication.restoreOverrideCursor()
