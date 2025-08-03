import importlib
import inspect
import os
import sys
import pkgutil
from typing import Dict, List, Any, Optional, Type, Callable
import abc
from pathlib import Path
from dotenv import load_dotenv

from py_backend_logic.core.logging_manager import get_logger

# Load environment variables
load_dotenv()

# Configure plugin settings
PLUGINS_ENABLED = os.getenv("PLUGINS_ENABLED", "true").lower() == "true"
PLUGINS_DIR = os.getenv("PLUGINS_DIR", "plugins")
PLUGIN_CONFIG_FILE = os.getenv("PLUGIN_CONFIG_FILE", "plugin_config.json")

# Create logger
logger = get_logger("plugin_system")

class PluginInterface(abc.ABC):
    """
    Base interface that all plugins must implement.
    """
    
    @abc.abstractmethod
    def get_name(self) -> str:
        """
        Get the name of the plugin.
        
        Returns:
            The plugin name
        """
        pass
    
    @abc.abstractmethod
    def get_version(self) -> str:
        """
        Get the version of the plugin.
        
        Returns:
            The plugin version
        """
        pass
    
    @abc.abstractmethod
    def get_description(self) -> str:
        """
        Get the description of the plugin.
        
        Returns:
            The plugin description
        """
        pass
    
    @abc.abstractmethod
    def initialize(self, app: Any, config: Dict[str, Any]) -> bool:
        """
        Initialize the plugin with the given configuration.
        
        Args:
            app: The FastAPI application instance
            config: Plugin configuration
            
        Returns:
            True if initialization was successful, False otherwise
        """
        pass
    
    @abc.abstractmethod
    def shutdown(self) -> None:
        """
        Perform cleanup when the plugin is being shut down.
        """
        pass
    
    def get_hooks(self) -> Dict[str, Callable]:
        """
        Get the hooks provided by this plugin.
        
        Returns:
            Dictionary mapping hook names to handler functions
        """
        return {}
    
    def get_middleware(self) -> List[Dict[str, Any]]:
        """
        Get middleware provided by this plugin.
        
        Returns:
            List of middleware configurations
        """
        return []
    
    def get_routes(self) -> List[Dict[str, Any]]:
        """
        Get routes provided by this plugin.
        
        Returns:
            List of route configurations
        """
        return []

class PluginManager:
    """
    Manages the discovery, loading, and lifecycle of plugins.
    """
    
    def __init__(self):
        """Initialize the plugin manager."""
        self.plugins: Dict[str, PluginInterface] = {}
        self.hooks: Dict[str, List[Callable]] = {}
        self.enabled = PLUGINS_ENABLED
        self.plugins_dir = Path(PLUGINS_DIR)
        
        # Create plugins directory if it doesn't exist
        if self.enabled:
            self.plugins_dir.mkdir(exist_ok=True)
            
            # Add plugins directory to Python path
            plugins_path = str(self.plugins_dir.absolute())
            if plugins_path not in sys.path:
                sys.path.append(plugins_path)
    
    def discover_plugins(self) -> List[str]:
        """
        Discover available plugins.
        
        Returns:
            List of discovered plugin module names
        """
        if not self.enabled:
            logger.info("Plugin system is disabled")
            return []
        
        discovered_plugins = []
        
        # Check if plugins directory exists
        if not self.plugins_dir.exists():
            logger.warning(f"Plugins directory not found: {self.plugins_dir}")
            return []
        
        logger.info(f"Discovering plugins in {self.plugins_dir}")
        
        # Discover plugin modules
        for finder, name, ispkg in pkgutil.iter_modules([str(self.plugins_dir)]):
            if ispkg:  # Only consider packages as plugins
                discovered_plugins.append(name)
                logger.info(f"Discovered plugin: {name}")
        
        return discovered_plugins
    
    def load_plugin(self, plugin_name: str) -> Optional[PluginInterface]:
        """
        Load a plugin by name.
        
        Args:
            plugin_name: Name of the plugin to load
            
        Returns:
            Plugin instance if successful, None otherwise
        """
        if not self.enabled:
            logger.warning(f"Cannot load plugin {plugin_name}: Plugin system is disabled")
            return None
        
        try:
            # Import the plugin module
            module_name = f"{plugin_name}"
            module = importlib.import_module(module_name)
            
            # Find plugin class (subclass of PluginInterface)
            plugin_class = None
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, PluginInterface) and 
                    obj is not PluginInterface):
                    plugin_class = obj
                    break
            
            if not plugin_class:
                logger.error(f"No plugin class found in {plugin_name}")
                return None
            
            # Create plugin instance
            plugin = plugin_class()
            logger.info(f"Loaded plugin: {plugin.get_name()} v{plugin.get_version()}")
            
            return plugin
            
        except Exception as e:
            logger.exception(f"Error loading plugin {plugin_name}: {str(e)}")
            return None
    
    def initialize_plugin(self, plugin: PluginInterface, app: Any, config: Dict[str, Any] = None) -> bool:
        """
        Initialize a plugin.
        
        Args:
            plugin: Plugin instance
            app: FastAPI application instance
            config: Plugin configuration
            
        Returns:
            True if initialization was successful, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            # Initialize the plugin
            plugin_name = plugin.get_name()
            logger.info(f"Initializing plugin: {plugin_name}")
            
            success = plugin.initialize(app, config or {})
            if not success:
                logger.error(f"Plugin {plugin_name} initialization failed")
                return False
            
            # Register plugin
            self.plugins[plugin_name] = plugin
            
            # Register hooks
            for hook_name, handler in plugin.get_hooks().items():
                if hook_name not in self.hooks:
                    self.hooks[hook_name] = []
                self.hooks[hook_name].append(handler)
            
            logger.info(f"Plugin {plugin_name} initialized successfully")
            return True
            
        except Exception as e:
            logger.exception(f"Error initializing plugin: {str(e)}")
            return False
    
    def load_and_initialize_plugins(self, app: Any, config: Dict[str, Any] = None) -> int:
        """
        Discover, load, and initialize all plugins.
        
        Args:
            app: FastAPI application instance
            config: Plugin configurations
            
        Returns:
            Number of successfully initialized plugins
        """
        if not self.enabled:
            logger.info("Plugin system is disabled")
            return 0
        
        # Discover plugins
        plugin_names = self.discover_plugins()
        if not plugin_names:
            logger.info("No plugins discovered")
            return 0
        
        # Load and initialize plugins
        initialized_count = 0
        for plugin_name in plugin_names:
            plugin = self.load_plugin(plugin_name)
            if plugin:
                plugin_config = config.get(plugin_name, {}) if config else {}
                if self.initialize_plugin(plugin, app, plugin_config):
                    initialized_count += 1
        
        logger.info(f"Initialized {initialized_count} plugins")
        return initialized_count
    
    def shutdown_plugins(self) -> None:
        """Shutdown all plugins."""
        if not self.enabled or not self.plugins:
            return
        
        logger.info(f"Shutting down {len(self.plugins)} plugins")
        
        for plugin_name, plugin in list(self.plugins.items()):
            try:
                logger.info(f"Shutting down plugin: {plugin_name}")
                plugin.shutdown()
                del self.plugins[plugin_name]
            except Exception as e:
                logger.exception(f"Error shutting down plugin {plugin_name}: {str(e)}")
    
    def get_plugin(self, name: str) -> Optional[PluginInterface]:
        """
        Get a plugin by name.
        
        Args:
            name: Plugin name
            
        Returns:
            Plugin instance if found, None otherwise
        """
        return self.plugins.get(name)
    
    def get_all_plugins(self) -> Dict[str, PluginInterface]:
        """
        Get all loaded plugins.
        
        Returns:
            Dictionary mapping plugin names to plugin instances
        """
        return self.plugins.copy()
    
    def call_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """
        Call all handlers for a specific hook.
        
        Args:
            hook_name: Name of the hook to call
            *args: Positional arguments to pass to handlers
            **kwargs: Keyword arguments to pass to handlers
            
        Returns:
            List of results from all hook handlers
        """
        if not self.enabled or hook_name not in self.hooks:
            return []
        
        results = []
        for handler in self.hooks[hook_name]:
            try:
                result = handler(*args, **kwargs)
                results.append(result)
            except Exception as e:
                logger.exception(f"Error in hook {hook_name}: {str(e)}")
        
        return results

# Create a singleton instance
plugin_manager = PluginManager()