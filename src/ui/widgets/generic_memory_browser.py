"""Generic Memory Browser Widget - Simplified Version.

Enhanced memory browser that works with the new GenericMemoryService
for flexible, user-defined collections instead of rigid types.
"""

import logging
import asyncio
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLineEdit, QPushButton,
    QComboBox, QSpinBox, QLabel, QTreeWidget, QTreeWidgetItem, QTextEdit,
    QTabWidget, QTableWidget, QTableWidgetItem, QFrame, QMessageBox,
    QCheckBox, QFormLayout, QDialog, QMenu
)
from PySide6.QtCore import QTimer, Signal, Qt
from PySide6.QtGui import QFont, QAction

# Import the new generic memory service
from ..services import MemoryService

logger = logging.getLogger(__name__)


class CreateCollectionDialog(QDialog):
    """Simple dialog for creating new collections."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Collection")
        self.setModal(True)
        self.resize(400, 300)
        self.collection_data = {}
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Form
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., my-project-notes")
        form_layout.addRow("Name:", self.name_input)
        
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Brief description")
        form_layout.addRow("Description:", self.description_input)
        
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("tag1, tag2, tag3")
        form_layout.addRow("Tags:", self.tags_input)
        
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            "custom", "project", "documentation", "code",
            "knowledge", "support", "personal"
        ])
        form_layout.addRow("Category:", self.category_combo)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        create_btn = QPushButton("Create Collection")
        create_btn.clicked.connect(self.create_collection)
        buttons_layout.addWidget(create_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
    
    def create_collection(self):
        """Create the collection."""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Collection name is required")
            return
            
        description = self.description_input.text().strip()
        tags = [
            tag.strip() for tag in self.tags_input.text().split(",")
            if tag.strip()
        ]
        category = self.category_combo.currentText()
        
        # Store data for parent to access
        self.collection_data = {
            "name": name,
            "description": description,
            "tags": tags,
            "category": category
        }
        
        self.accept()


class GenericMemoryBrowserWidget(QWidget):
    """
    Enhanced memory browser supporting flexible collections.
    
    Features:
    - Dynamic collection creation and management
    - Flexible search across any collections
    - Collection-based organization instead of rigid types
    """

    memory_selected = Signal(dict)
    collection_created = Signal(dict)
    collection_deleted = Signal(str)

    def __init__(self, server_url: str = "generic"):
        super().__init__()
        self.server_url = server_url
        self.collections = []
        self.current_results = []
        
        # Initialize memory service
        self.memory_service = None
        if MemoryService is not None:
            self.memory_service = MemoryService(server_url)
        
        self.setup_ui()
        self.setup_connections()
        self.setup_timer()
        
        # Start with a delay to allow service initialization
        self._startup_timer = QTimer()
        self._startup_timer.setSingleShot(True)
        self._startup_timer.timeout.connect(self.initialize_service)
        self._startup_timer.start(2000)  # 2 second delay
        
        # Auto-migration flag
        self._auto_migration_attempted = False

    def setup_ui(self):
        """Set up the enhanced memory browser UI."""
        layout = QVBoxLayout(self)
        
        # Status bar
        self.setup_status_bar(layout)
        
        # Collection management
        self.setup_collection_management(layout)
        
        # Search controls
        self.setup_search_controls(layout)
        
        # Main content tabs
        self.setup_main_content(layout)

    def setup_status_bar(self, layout):
        """Set up connection status and controls."""
        status_frame = QFrame()
        status_frame.setFrameStyle(QFrame.StyledPanel)
        status_frame.setMaximumHeight(40)
        status_layout = QHBoxLayout(status_frame)
        
        self.status_label = QLabel("Memory: Initializing...")
        self.status_label.setStyleSheet(
            "QLabel { color: orange; font-weight: bold; padding: 4px; }"
        )
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_data)
        self.refresh_btn.setMaximumWidth(80)
        status_layout.addWidget(self.refresh_btn)
        
        layout.addWidget(status_frame)

    def setup_collection_management(self, layout):
        """Set up collection management controls."""
        management_group = QGroupBox("Collection Management")
        management_layout = QHBoxLayout(management_group)
        
        self.collections_combo = QComboBox()
        self.collections_combo.setMinimumWidth(200)
        management_layout.addWidget(QLabel("Active Collection:"))
        management_layout.addWidget(self.collections_combo)
        
        # Collection actions
        self.create_collection_btn = QPushButton("+ New Collection")
        self.create_collection_btn.clicked.connect(
            self.show_create_collection_dialog
        )
        management_layout.addWidget(self.create_collection_btn)
        
        self.delete_collection_btn = QPushButton("Delete")
        self.delete_collection_btn.clicked.connect(
            self.delete_current_collection
        )
        self.delete_collection_btn.setStyleSheet(
            "QPushButton { color: red; }"
        )
        management_layout.addWidget(self.delete_collection_btn)
        
        management_layout.addStretch()
        
        layout.addWidget(management_group)

    def setup_search_controls(self, layout):
        """Set up enhanced search interface."""
        search_group = QGroupBox("Memory Search")
        search_layout = QVBoxLayout(search_group)
        
        # Search input
        search_row = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Search across your collections..."
        )
        self.search_input.returnPressed.connect(self.perform_search)
        search_row.addWidget(self.search_input)
        
        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self.perform_search)
        search_row.addWidget(self.search_btn)
        
        search_layout.addLayout(search_row)
        
        # Search options
        options_row = QHBoxLayout()
        
        # Multi-collection search
        self.search_all_cb = QCheckBox("Search all collections")
        self.search_all_cb.setChecked(True)
        options_row.addWidget(self.search_all_cb)
        
        options_row.addWidget(QLabel("Limit:"))
        self.limit_spin = QSpinBox()
        self.limit_spin.setRange(1, 100)
        self.limit_spin.setValue(10)
        options_row.addWidget(self.limit_spin)
        
        options_row.addStretch()
        
        search_layout.addLayout(options_row)
        layout.addWidget(search_group)

    def setup_main_content(self, layout):
        """Set up main tabbed content area."""
        self.tab_widget = QTabWidget()
        
        # Search Results tab
        self.setup_results_tab()
        
        # Collections tab
        self.setup_collections_tab()
        
        # Add Memory tab
        self.setup_add_memory_tab()
        
        # Statistics tab
        self.setup_statistics_tab()
        
        layout.addWidget(self.tab_widget)

    def setup_results_tab(self):
        """Set up search results display."""
        results_widget = QWidget()
        results_layout = QVBoxLayout(results_widget)
        
        # Results header
        header_layout = QHBoxLayout()
        self.results_label = QLabel("No search performed")
        header_layout.addWidget(self.results_label)
        header_layout.addStretch()
        
        self.clear_results_btn = QPushButton("Clear")
        self.clear_results_btn.clicked.connect(self.clear_results)
        header_layout.addWidget(self.clear_results_btn)
        
        results_layout.addLayout(header_layout)
        
        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels([
            "Score", "Content", "Collection", "Tags"
        ])
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        results_layout.addWidget(self.results_table)
        
        self.tab_widget.addTab(results_widget, "Search Results")

    def setup_collections_tab(self):
        """Set up collections management display."""
        collections_widget = QWidget()
        collections_layout = QVBoxLayout(collections_widget)
        
        # Collections tree
        self.collections_tree = QTreeWidget()
        self.collections_tree.setHeaderLabels([
            "Collection", "Description", "Documents", "Category", "Tags"
        ])
        
        # Enable context menu
        self.collections_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.collections_tree.customContextMenuRequested.connect(
            self.show_collections_context_menu
        )
        
        collections_layout.addWidget(self.collections_tree)
        
        # Collection actions
        actions_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Refresh Collections")
        refresh_btn.clicked.connect(self.refresh_collections)
        actions_layout.addWidget(refresh_btn)
        
        actions_layout.addStretch()
        collections_layout.addLayout(actions_layout)
        
        self.tab_widget.addTab(collections_widget, "Collections")

    def setup_add_memory_tab(self):
        """Set up add memory interface."""
        add_widget = QWidget()
        add_layout = QVBoxLayout(add_widget)
        
        # Collection selection
        collection_row = QHBoxLayout()
        collection_row.addWidget(QLabel("Add to Collection:"))
        
        self.add_collection_combo = QComboBox()
        collection_row.addWidget(self.add_collection_combo)
        
        collection_row.addStretch()
        add_layout.addLayout(collection_row)
        
        # Content input
        self.content_input = QTextEdit()
        self.content_input.setPlaceholderText(
            "Enter content to add to memory...\n\n"
            "This can be notes, code snippets, documentation, "
            "or any other information you want to store and search later."
        )
        add_layout.addWidget(self.content_input)
        
        # Tags input
        tags_row = QHBoxLayout()
        tags_row.addWidget(QLabel("Tags:"))
        self.add_tags_input = QLineEdit()
        self.add_tags_input.setPlaceholderText("tag1, tag2, tag3")
        tags_row.addWidget(self.add_tags_input)
        add_layout.addLayout(tags_row)
        
        # Add button
        add_btn = QPushButton("Add Memory")
        add_btn.clicked.connect(self.add_memory)
        add_layout.addWidget(add_btn)
        
        self.tab_widget.addTab(add_widget, "Add Memory")

    def setup_statistics_tab(self):
        """Set up statistics display."""
        stats_widget = QWidget()
        stats_layout = QVBoxLayout(stats_widget)
        
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setFont(QFont("monospace"))
        stats_layout.addWidget(self.stats_text)
        
        refresh_stats_btn = QPushButton("Refresh Statistics")
        refresh_stats_btn.clicked.connect(self.refresh_stats)
        stats_layout.addWidget(refresh_stats_btn)
        
        self.tab_widget.addTab(stats_widget, "Statistics")

    def setup_connections(self):
        """Set up signal connections."""
        # Collection combo selection
        self.collections_combo.currentTextChanged.connect(
            self.on_collection_changed
        )

    def setup_timer(self):
        """Set up periodic refresh timer."""
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_stats)
        self.timer.start(30000)  # Refresh every 30 seconds

    # Core functionality

    def initialize_service(self):
        """Initialize the memory service."""
        if self.memory_service:
            # Use asyncio to initialize
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                success = loop.run_until_complete(
                    self.memory_service.initialize(local_mode=True)
                )
                loop.close()
                
                if success:
                    self.status_label.setText("Memory: Connected")
                    self.status_label.setStyleSheet(
                        "QLabel { color: green; font-weight: bold; padding: 4px; }"
                    )
                    self.refresh_data()
                    # Auto-migrate legacy data if no collections exist
                    self.auto_migrate_if_needed()
                else:
                    self.status_label.setText("Memory: Failed")
                    self.status_label.setStyleSheet(
                        "QLabel { color: red; font-weight: bold; padding: 4px; }"
                    )
                    
            except Exception as e:
                logger.error(f"Failed to initialize memory service: {e}")
                self.status_label.setText("Memory: Error")
                self.status_label.setStyleSheet(
                    "QLabel { color: red; font-weight: bold; padding: 4px; }"
                )

    def refresh_data(self):
        """Refresh all data."""
        self.refresh_collections()
        self.refresh_stats()

    def refresh_collections(self):
        """Refresh collections list."""
        if not self.memory_service or not self.memory_service._ensure_initialized():
            return
            
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            collections = loop.run_until_complete(
                self.memory_service.get_collections()
            )
            loop.close()
            
            self.collections = collections
            self.update_collections_ui()
            
        except Exception as e:
            logger.error(f"Failed to refresh collections: {e}")

    def update_collections_ui(self):
        """Update UI with current collections."""
        # Update combo boxes
        current_collection = self.collections_combo.currentText()
        
        self.collections_combo.clear()
        self.add_collection_combo.clear()
        
        collection_names = [col["name"] for col in self.collections]
        
        self.collections_combo.addItems(collection_names)
        self.add_collection_combo.addItems(collection_names)
        
        # Restore selection
        if current_collection in collection_names:
            self.collections_combo.setCurrentText(current_collection)
        
        # Update collections tree
        self.collections_tree.clear()
        for col in self.collections:
            item = QTreeWidgetItem([
                col["name"],
                col.get("description", ""),
                str(col.get("documents", 0)),
                col.get("type", "custom"),
                ", ".join(col.get("tags", []))
            ])
            self.collections_tree.addTopLevelItem(item)

    def show_create_collection_dialog(self):
        """Show collection creation dialog."""
        dialog = CreateCollectionDialog(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.collection_data
            self.create_collection_async(data)

    def create_collection_async(self, data):
        """Create collection asynchronously."""
        if not self.memory_service:
            QMessageBox.warning(self, "Error", "Memory service not available")
            return
            
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(
                self.memory_service.create_collection(**data)
            )
            loop.close()
            
            if result.get("success"):
                QMessageBox.information(
                    self, "Success", f"Collection '{data['name']}' created!"
                )
                self.refresh_collections()
                self.collection_created.emit(result)
            else:
                error_msg = result.get('error', 'Unknown error')
                QMessageBox.critical(
                    self, "Error", f"Failed to create collection: {error_msg}"
                )
                
        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            QMessageBox.critical(
                self, "Error", f"Failed to create collection: {str(e)}"
            )

    def perform_search(self):
        """Perform memory search."""
        query = self.search_input.text().strip()
        if not query:
            return
            
        if not self.memory_service or not self.memory_service._ensure_initialized():
            QMessageBox.warning(self, "Error", "Memory service not available")
            return
        
        try:
            self.search_btn.setEnabled(False)
            self.results_label.setText("Searching...")
            
            # Determine collections to search
            collections = None
            if not self.search_all_cb.isChecked():
                current_collection = self.collections_combo.currentText()
                if current_collection:
                    collections = [current_collection]
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            results = loop.run_until_complete(
                self.memory_service.search_memory(
                    query=query,
                    collections=collections,
                    limit=self.limit_spin.value()
                )
            )
            loop.close()
            
            self.display_search_results(results, query)
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            QMessageBox.critical(self, "Search Error", str(e))
        finally:
            self.search_btn.setEnabled(True)

    def display_search_results(self, results, query):
        """Display search results in table."""
        self.current_results = results
        self.results_table.setRowCount(len(results))
        
        for row, result in enumerate(results):
            # Score
            score = result.get("score", 0.0)
            score_item = QTableWidgetItem(f"{score:.3f}")
            self.results_table.setItem(row, 0, score_item)
            
            # Content preview
            content = result.get("payload", {}).get("content", "")
            if len(content) > 100:
                content = content[:100] + "..."
            content_item = QTableWidgetItem(content)
            self.results_table.setItem(row, 1, content_item)
            
            # Collection
            collection = result.get("collection", "Unknown")
            collection_item = QTableWidgetItem(collection)
            self.results_table.setItem(row, 2, collection_item)
            
            # Tags
            tags = result.get("payload", {}).get("tags", [])
            tags_item = QTableWidgetItem(", ".join(tags))
            self.results_table.setItem(row, 3, tags_item)
        
        self.results_label.setText(f"Found {len(results)} results for '{query}'")
        self.results_table.resizeColumnsToContents()

    def add_memory(self):
        """Add memory to selected collection."""
        content = self.content_input.toPlainText().strip()
        if not content:
            QMessageBox.warning(self, "Error", "Please enter content to add")
            return
            
        collection = self.add_collection_combo.currentText()
        if not collection:
            QMessageBox.warning(self, "Error", "Please select a collection")
            return
            
        if not self.memory_service or not self.memory_service._ensure_initialized():
            QMessageBox.warning(self, "Error", "Memory service not available")
            return
        
        try:
            # Parse tags
            tags_text = self.add_tags_input.text().strip()
            tags = [tag.strip() for tag in tags_text.split(",") if tag.strip()]
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(
                self.memory_service.add_memory(
                    collection=collection,
                    content=content,
                    tags=tags
                )
            )
            loop.close()
            
            if result.get("success"):
                QMessageBox.information(
                    self, "Success", f"Memory added to '{collection}'"
                )
                self.content_input.clear()
                self.add_tags_input.clear()
                self.refresh_stats()
            else:
                error_msg = result.get('error', 'Unknown error')
                QMessageBox.critical(
                    self, "Error", f"Failed to add memory: {error_msg}"
                )
                
        except Exception as e:
            logger.error(f"Failed to add memory: {e}")
            QMessageBox.critical(
                self, "Error", f"Failed to add memory: {str(e)}"
            )

    def auto_migrate_if_needed(self):
        """Auto-migrate legacy collections if no generic collections exist."""
        if self._auto_migration_attempted:
            return
            
        self._auto_migration_attempted = True
        
        # Check if we have any collections
        if len(self.collections) == 0:
            logger.info(
                "No generic collections found, attempting auto-migration..."
            )
            
            # Auto-migrate in the background
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                result = loop.run_until_complete(
                    self.memory_service.migrate_legacy_collections()
                )
                loop.close()
                
                if result.get("success"):
                    logger.info("Auto-migration completed successfully")
                    self.refresh_data()  # Refresh to show migrated collections
                else:
                    logger.info("Auto-migration not needed or failed")
                    # Create some example collections if none exist
                    self.create_default_collections()
                    
            except Exception as e:
                logger.error(f"Auto-migration failed: {e}")
                self.create_default_collections()

    def create_default_collections(self):
        """Create some default collections for new users."""
        default_collections = [
            {
                "name": "general-notes",
                "description": "General notes and information",
                "tags": ["notes", "general"],
                "category": "custom"
            },
            {
                "name": "project-ideas",
                "description": "Project ideas and concepts",
                "tags": ["projects", "ideas"],
                "category": "project"
            }
        ]
        
        for col_data in default_collections:
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                result = loop.run_until_complete(
                    self.memory_service.create_collection(**col_data)
                )
                loop.close()
                
                if result.get("success"):
                    logger.info(
                        f"Created default collection: {col_data['name']}"
                    )
                    
            except Exception as e:
                logger.error(
                    f"Failed to create default collection {col_data['name']}: {e}"
                )
        
        # Refresh collections after creating defaults
        self.refresh_collections()

    def refresh_stats(self):
        """Refresh memory statistics."""
        if not self.memory_service or not self.memory_service._ensure_initialized():
            return
            
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            stats = loop.run_until_complete(
                self.memory_service.get_stats()
            )
            loop.close()
            
            self.display_stats(stats)
            
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")

    def display_stats(self, stats):
        """Display statistics in text widget."""
        if not stats:
            return
            
        stats_text = "Generic Memory System Statistics\n"
        stats_text += "=" * 50 + "\n\n"
        
        # Overall stats
        stats_text += f"Status: {stats.get('status', 'unknown')}\n"
        stats_text += f"Total Collections: {stats.get('total_collections', 0)}\n"
        stats_text += f"Total Documents: {stats.get('total_documents', 0)}\n"
        stats_text += f"Total Vectors: {stats.get('total_vectors', 0)}\n\n"
        
        # Per-collection stats
        collections = stats.get("collections", {})
        if collections:
            stats_text += "Collections Breakdown:\n"
            stats_text += "-" * 30 + "\n"
            
            for name, col_stats in collections.items():
                stats_text += f"\n{name}:\n"
                stats_text += f"  Documents: {col_stats.get('documents', 0)}\n"
                stats_text += f"  Vectors: {col_stats.get('vectors', 0)}\n"
                stats_text += f"  Category: {col_stats.get('category', 'custom')}\n"
                tags = col_stats.get('tags', [])
                if tags:
                    stats_text += f"  Tags: {', '.join(tags)}\n"
        
        # Last updated
        last_updated = stats.get('last_updated', '')
        if last_updated:
            try:
                dt = datetime.fromisoformat(last_updated.replace("Z", "+00:00"))
                formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                stats_text += f"\n\nLast Updated: {formatted_time}"
            except:
                stats_text += f"\n\nLast Updated: {last_updated}"
        
        self.stats_text.setPlainText(stats_text)


    # Event handlers
    
    def on_collection_changed(self, collection_name):
        """Handle collection selection change."""
        if collection_name:
            logger.info(f"Selected collection: {collection_name}")

    def clear_results(self):
        """Clear search results."""
        self.results_table.setRowCount(0)
        self.current_results = []
        self.results_label.setText("No search performed")

    def delete_current_collection(self):
        """Delete the currently selected collection."""
        collection_name = self.collections_combo.currentText()
        if not collection_name:
            QMessageBox.warning(self, "Error", "No collection selected")
            return
        
        reply = QMessageBox.question(
            self, "Delete Collection",
            f"Are you sure you want to delete collection '{collection_name}'?\n\n"
            "This will permanently delete all memories in this collection.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        if not self.memory_service or not self.memory_service._ensure_initialized():
            QMessageBox.warning(self, "Error", "Memory service not available")
            return
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(
                self.memory_service.delete_collection(
                    name=collection_name, confirm=True
                )
            )
            loop.close()
            
            if result.get("success"):
                QMessageBox.information(
                    self, "Success", f"Collection '{collection_name}' deleted"
                )
                self.refresh_collections()
                self.collection_deleted.emit(collection_name)
            else:
                error_msg = result.get('error', 'Unknown error')
                QMessageBox.critical(
                    self, "Error", f"Failed to delete: {error_msg}"
                )
                
        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")
            QMessageBox.critical(self, "Error", str(e))

    def show_collections_context_menu(self, position):
        """Show context menu for collections tree."""
        item = self.collections_tree.itemAt(position)
        if not item:
            return
            
        # Get collection name from the first column
        collection_name = item.text(0)
        if not collection_name:
            return
            
        # Create context menu
        context_menu = QMenu(self)
        
        # Delete action
        delete_action = QAction("Delete Collection", self)
        delete_action.triggered.connect(
            lambda: self.delete_collection_from_tree(collection_name)
        )
        context_menu.addAction(delete_action)
        
        # Show the context menu
        context_menu.exec_(self.collections_tree.mapToGlobal(position))

    def delete_collection_from_tree(self, collection_name):
        """Delete a collection selected from the tree context menu."""
        if not collection_name:
            QMessageBox.warning(self, "Error", "No collection selected")
            return
        
        reply = QMessageBox.question(
            self, "Delete Collection",
            f"Are you sure you want to delete collection '{collection_name}'?\n\n"
            "This will permanently delete all memories in this collection.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        if not self.memory_service or not self.memory_service._ensure_initialized():
            QMessageBox.warning(self, "Error", "Memory service not available")
            return
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(
                self.memory_service.delete_collection(
                    name=collection_name, confirm=True
                )
            )
            loop.close()
            
            if result.get("success"):
                QMessageBox.information(
                    self, "Success", f"Collection '{collection_name}' deleted"
                )
                self.refresh_collections()
                self.collection_deleted.emit(collection_name)
            else:
                error_msg = result.get('error', 'Unknown error')
                QMessageBox.critical(
                    self, "Error", f"Failed to delete: {error_msg}"
                )
                
        except Exception as e:
            logger.error(f"Failed to delete collection from tree: {e}")
            QMessageBox.critical(self, "Error", str(e))