"""
Configuration utilities for eodata-gateway
"""
import os
import yaml
from pathlib import Path


def load_yaml_config(config_path):
    """
    Load a YAML configuration file
    
    Args:
        config_path (str): Path to the YAML configuration file
        
    Returns:
        dict: Configuration dictionary
    """
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config


def get_config_path(config_name):
    """
    Get the absolute path to a configuration file
    
    Args:
        config_name (str): Name of the configuration file (without extension)
        
    Returns:
        str: Absolute path to the configuration file
    """
    # Get the directory of this file
    current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(current_dir, f"{config_name}.yml")


def load_opensearch_provider_config(config_path=None):
    """
    Load the OpenSearch provider configuration
    
    Args:
        config_path (str, optional): Path to the configuration file.
            If None, the default configuration file will be used.
            
    Returns:
        dict: OpenSearch provider configuration
    """
    if config_path is None:
        config_path = get_config_path("opensearch_provider")
    
    return load_yaml_config(config_path)
