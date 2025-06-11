# EODAG with OpenSearch Plugins for Copernicus Dataspace
# Using built-in EODAG plugins for OpenSearch protocol

import os
import yaml
from datetime import datetime, timedelta
from eodag import EODataAccessGateway
from eodag.config import load_default_config

# =============================================================================
# 1. EODAG OPENSEARCH PLUGINS CONFIGURATION
# =============================================================================

def create_opensearch_provider_config():
    """
    Create EODAG provider configuration using OpenSearch plugins
    
    EODAG Plugin Architecture:
    - SearchPlugin: eodag.plugins.search.qssearch.QueryStringSearch (OpenSearch)
    - DownloadPlugin: eodag.plugins.download.http.HTTPDownload
    - AuthPlugin: eodag.plugins.authentication.oauth.OAuth2AuthorizationCodeFlow
    """
    
    config = {
        'cop_dataspace': {
            'priority': 1,
            'description': 'Copernicus Dataspace with OpenSearch API',
            
            # Search plugin configuration (OpenSearch)
            'search': {
                'plugin': 'QueryStringSearch',  # Built-in OpenSearch plugin
                'api_endpoint': 'https://catalogue.dataspace.copernicus.eu/resto/api/collections/{collection}/search.json',
                'pagination': {
                    'next_page_query_obj': '{{"page": {page}, "maxRecords": {items_per_page}}}',
                    'total_items_nb_key_path': '$.properties.totalResults'
                },
                'discover_metadata': {
                    'auto_discovery': True,
                    'metadata_pattern': 'https://catalogue.dataspace.copernicus.eu/resto/api/collections/{collection}/describe.xml',
                    'search_param': 'q'
                },
                'free_text_search_operations': {
                    'union': ' OR ',
                    'intersection': ' AND ',
                    'difference': ' NOT '
                },
                'literal_search_params': {
                    'format': 'json'
                },
                'constraints_file_url': 'https://catalogue.dataspace.copernicus.eu/resto/api/collections/describe.xml'
            },
            
            # Download plugin configuration
            'download': {
                'plugin': 'HTTPDownload',  # Built-in HTTP download plugin
                'base_uri': 'https://zipper.dataspace.copernicus.eu/odata/v1',
                'extract': False,
                'archive_depth': 1,
                'dl_url_params': {
                    '$format': 'json'
                },
                'timeout': 300,
                'chunk_size': 8192
            },
            
            # Authentication plugin configuration
            'auth': {
                'plugin': 'OAuth2ResourceOwnerPasswordCredentialsFlow',  # OAuth2 plugin
                'token_provision': 'header',
                'token_qs_key': 'access_token',
                'auth_uri': 'https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token',
                'client_id': 'cdse-public',
                'client_secret': '',  # Public client
                'resource_owner_key': 'username',
                'resource_owner_secret': 'password',
                'token_exchange_post_data_method': 'json',
                'token_exchange_params': {
                    'grant_type': 'password',
                    'client_id': 'cdse-public'
                },
                'credentials': {
                    'username': '${COPERNICUS_USERNAME}',
                    'password': '${COPERNICUS_PASSWORD}'
                }
            },
            
            # Product type mapping
            'products': {
                # Sentinel-1 products
                'S1_SAR_GRD': {
                    'collection': 'SENTINEL-1',
                    'productType': 'GRD',
                    'polarisation': '{polarisation}',
                    'sensorMode': '{sensorMode}',
                    'resolution': '{resolution}'
                },
                'S1_SAR_SLC': {
                    'collection': 'SENTINEL-1',
                    'productType': 'SLC',
                    'polarisation': '{polarisation}',
                    'sensorMode': '{sensorMode}'
                },
                'S1_SAR_OCN': {
                    'collection': 'SENTINEL-1',
                    'productType': 'OCN',
                    'polarisation': '{polarisation}',
                    'sensorMode': '{sensorMode}'
                },
                
                # Sentinel-2 products  
                'S2_MSI_L1C': {
                    'collection': 'SENTINEL-2',
                    'productType': 'S2MSI1C',
                    'processingLevel': 'LEVEL1C',
                    'cloudCover': '{cloudCover}'
                },
                'S2_MSI_L2A': {
                    'collection': 'SENTINEL-2',
                    'productType': 'S2MSI2A',
                    'processingLevel': 'LEVEL2A',
                    'cloudCover': '{cloudCover}'
                },
                
                # Sentinel-3 products
                'S3_OLCI_L1_EFR': {
                    'collection': 'SENTINEL-3',
                    'productType': 'OL_1_EFR___',
                    'instrument': 'OLCI'
                },
                'S3_OLCI_L2_LFR': {
                    'collection': 'SENTINEL-3',
                    'productType': 'OL_2_LFR___',
                    'instrument': 'OLCI'
                },
                'S3_SLSTR_L1_RBT': {
                    'collection': 'SENTINEL-3',
                    'productType': 'SL_1_RBT___',
                    'instrument': 'SLSTR'
                },
                'S3_SLSTR_L2_LST': {
                    'collection': 'SENTINEL-3',
                    'productType': 'SL_2_LST___',
                    'instrument': 'SLSTR'
                },
                
                # Sentinel-5P products
                'S5P_L1B_IR_SIR': {
                    'collection': 'SENTINEL-5P',
                    'productType': 'L1B_IR_SIR',
                    'instrument': 'TROPOMI'
                },
                'S5P_L2_CH4': {
                    'collection': 'SENTINEL-5P',
                    'productType': 'L2__CH4___',
                    'instrument': 'TROPOMI'
                },
                'S5P_L2_CO': {
                    'collection': 'SENTINEL-5P',
                    'productType': 'L2__CO____',
                    'instrument': 'TROPOMI'
                },
                'S5P_L2_NO2': {
                    'collection': 'SENTINEL-5P',
                    'productType': 'L2__NO2___',
                    'instrument': 'TROPOMI'
                },
                'S5P_L2_O3': {
                    'collection': 'SENTINEL-5P',
                    'productType': 'L2__O3____',
                    'instrument': 'TROPOMI'
                },
                'S5P_L2_SO2': {
                    'collection': 'SENTINEL-5P',
                    'productType': 'L2__SO2___',
                    'instrument': 'TROPOMI'
                }
            }
        }
    }
    
    return config

# =============================================================================
# 2. EODAG SETUP WITH OPENSEARCH PLUGINS
# =============================================================================

def setup_eodag_opensearch():
    """Setup EODAG with OpenSearch plugins configuration"""
    
    # Create the configuration
    config = {'providers': create_opensearch_provider_config()}
    
    # Initialize EODAG with custom configuration
    dag = EODataAccessGateway()
    dag.update_providers_config(config['providers'])
    
    # Set preferred provider
    dag.set_preferred_provider('cop_dataspace')
    
    print("✓ EODAG configured with OpenSearch plugins")
    print(f"✓ Available providers: {dag.available_providers()}")
    
    return dag

def create_yaml_config():
    """Create and save YAML configuration file"""
    
    config = {
        'providers': create_opensearch_provider_config()
    }
    
    # Save to YAML file
    config_file = 'eodag_opensearch_config.yml'
    with open(config_file, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    print(f"✓ Configuration saved to {config_file}")
    return config_file

def load_from_yaml_config():
    """Load EODAG from YAML configuration file"""
    
    config_file = 'eodag_opensearch_config.yml'
    
    if not os.path.exists(config_file):
        print("Creating configuration file...")
        create_yaml_config()
    
    # Load EODAG with configuration file
    dag = EODataAccessGateway(user_conf_file_path=config_file)
    dag.set_preferred_provider('cop_dataspace')
    
    return dag

# =============================================================================
# 3. PLUGIN INSPECTION AND DEBUGGING
# =============================================================================

def inspect_plugins():
    """Inspect available EODAG plugins"""
    
    dag = EODataAccessGateway()
    
    # Get all available plugins
    print("=== Available EODAG Plugins ===")
    
    # Search plugins
    print("\nSearch Plugins:")
    try:
        from eodag.plugins.search import SEARCH_PLUGINS
        for name, plugin_class in SEARCH_PLUGINS.items():
            print(f"  - {name}: {plugin_class}")
    except ImportError:
        print("  Could not import search plugins")
    
    # Download plugins  
    print("\nDownload Plugins:")
    try:
        from eodag.plugins.download import DOWNLOAD_PLUGINS
        for name, plugin_class in DOWNLOAD_PLUGINS.items():
            print(f"  - {name}: {plugin_class}")
    except ImportError:
        print("  Could not import download plugins")
    
    # Authentication plugins
    print("\nAuthentication Plugins:")
    try:
        from eodag.plugins.authentication import AUTHENTICATION_PLUGINS
        for name, plugin_class in AUTHENTICATION_PLUGINS.items():
            print(f"  - {name}: {plugin_class}")
    except ImportError:
        print("  Could not import authentication plugins")

def debug_provider_config():
    """Debug provider configuration"""
    
    dag = setup_eodag_opensearch()
    
    print("\n=== Provider Configuration Debug ===")
    
    # Get provider configuration
    provider_config = dag.providers_config.get('cop_dataspace', {})
    
    print(f"Provider: cop_dataspace")
    print(f"Priority: {provider_config.get('priority', 'Not set')}")
    
    # Search plugin info
    search_config = provider_config.get('search', {})
    print(f"Search Plugin: {search_config.get('plugin', 'Not set')}")
    print(f"API Endpoint: {search_config.get('api_endpoint', 'Not set')}")
    
    # Download plugin info
    download_config = provider_config.get('download', {})
    print(f"Download Plugin: {download_config.get('plugin', 'Not set')}")
    print(f"Base URI: {download_config.get('base_uri', 'Not set')}")
    
    # Auth plugin info
    auth_config = provider_config.get('auth', {})
    print(f"Auth Plugin: {auth_config.get('plugin', 'Not set')}")
    print(f"Auth URI: {auth_config.get('auth_uri', 'Not set')}")

# =============================================================================
# 4. SEARCH EXAMPLES WITH OPENSEARCH PLUGINS
# =============================================================================

def search_sentinel2_opensearch():
    """Search Sentinel-2 data using OpenSearch plugins"""
    
    print("\n=== Sentinel-2 Search with OpenSearch Plugins ===")
    
    dag = setup_eodag_opensearch()
    
    # Search parameters
    search_criteria = {
        'productType': 'S2_MSI_L2A',
        'start': datetime.now() - timedelta(days=30),
        'end': datetime.now(),
        'geom': {
            'lonmin': 2.0,   # Paris area
            'latmin': 48.5,
            'lonmax': 2.8,
            'latmax': 49.0
        },
        'cloudCover': 20,
        'items_per_page': 10
    }
    
    try:
        # Perform search
        print("🔍 Searching for Sentinel-2 products...")
        products = dag.search(**search_criteria)
        
        print(f"✓ Found {len(products)} products")
        
        # Display results
        for i, product in enumerate(products[:5]):
            props = product.properties
            print(f"\nProduct {i+1}:")
            print(f"  ID: {props.get('id', 'N/A')}")
            print(f"  Title: {props.get('title', 'N/A')}")
            print(f"  Date: {props.get('datetime', 'N/A')}")
            print(f"  Cloud Cover: {props.get('eo:cloud_cover', 'N/A')}%")
            print(f"  Platform: {props.get('platform', 'N/A')}")
            print(f"  Collection: {props.get('collection', 'N/A')}")
        
        return products
        
    except Exception as e:
        print(f"✗ Search failed: {e}")
        print("Make sure your credentials are set:")
        print("  export COPERNICUS_USERNAME='your_username'")
        print("  export COPERNICUS_PASSWORD='your_password'")
        return []

def search_sentinel1_opensearch():
    """Search Sentinel-1 SAR data using OpenSearch plugins"""
    
    print("\n=== Sentinel-1 SAR Search with OpenSearch Plugins ===")
    
    dag = setup_eodag_opensearch()
    
    # Search parameters
    search_criteria = {
        'productType': 'S1_SAR_GRD',
        'start': datetime.now() - timedelta(days=15),
        'end': datetime.now(),
        'geom': {
            'lonmin': 2.0,
            'latmin': 48.5,
            'lonmax': 2.8,
            'latmax': 49.0
        },
        'sensorMode': 'IW',  # Interferometric Wide swath
        'polarisation': 'VV VH',
        'items_per_page': 5
    }
    
    try:
        print("🔍 Searching for Sentinel-1 SAR products...")
        products = dag.search(**search_criteria)
        
        print(f"✓ Found {len(products)} products")
        
        for i, product in enumerate(products[:3]):
            props = product.properties
            print(f"\nProduct {i+1}:")
            print(f"  ID: {props.get('id', 'N/A')}")
            print(f"  Title: {props.get('title', 'N/A')}")
            print(f"  Date: {props.get('datetime', 'N/A')}")
            print(f"  Sensor Mode: {props.get('sar:instrument_mode', 'N/A')}")
            print(f"  Polarisation: {props.get('sar:polarizations', 'N/A')}")
            print(f"  Orbit: {props.get('sat:orbit_state', 'N/A')}")
        
        return products
        
    except Exception as e:
        print(f"✗ Search failed: {e}")
        return []

def search_sentinel5p_opensearch():
    """Search Sentinel-5P atmospheric data using OpenSearch plugins"""
    
    print("\n=== Sentinel-5P Atmospheric Search with OpenSearch Plugins ===")
    
    dag = setup_eodag_opensearch()
    
    # Search parameters
    search_criteria = {
        'productType': 'S5P_L2_NO2',  # Nitrogen Dioxide
        'start': datetime.now() - timedelta(days=7),
        'end': datetime.now(),
        'geom': {
            'lonmin': 2.0,
            'latmin': 48.5,
            'lonmax': 2.8,
            'latmax': 49.0
        },
        'items_per_page': 5
    }
    
    try:
        print("🔍 Searching for Sentinel-5P NO2 products...")
        products = dag.search(**search_criteria)
        
        print(f"✓ Found {len(products)} products")
        
        for i, product in enumerate(products[:3]):
            props = product.properties
            print(f"\nProduct {i+1}:")
            print(f"  ID: {props.get('id', 'N/A')}")
            print(f"  Title: {props.get('title', 'N/A')}")
            print(f"  Date: {props.get('datetime', 'N/A')}")
            print(f"  Instrument: {props.get('instrument', 'N/A')}")
            print(f"  Processing Level: {props.get('processing:level', 'N/A')}")
        
        return products
        
    except Exception as e:
        print(f"✗ Search failed: {e}")
        return []

# =============================================================================
# 5. DOWNLOAD EXAMPLES WITH OPENSEARCH PLUGINS
# =============================================================================

def download_with_opensearch_plugins():
    """Download products using OpenSearch plugins"""
    
    print("\n=== Download with OpenSearch Plugins ===")
    
    dag = setup_eodag_opensearch()
    
    # Search for a small product first
    search_criteria = {
        'productType': 'S2_MSI_L2A',
        'start': datetime.now() - timedelta(days=7),
        'end': datetime.now(),
        'geom': {
            'lonmin': 2.2,
            'latmin': 48.8,
            'lonmax': 2.4,
            'latmax': 49.0
        },
        'cloudCover': 5,
        'items_per_page': 1
    }
    
    try:
        products = dag.search(**search_criteria)
        
        if products:
            product = products[0]
            print(f"📦 Downloading: {product.properties.get('title', 'Unknown')}")
            print(f"📏 Size: {product.properties.get('size', 'Unknown')}")
            
            # Create download directory
            download_dir = "./downloads"
            os.makedirs(download_dir, exist_ok=True)
            
            # Download (uncomment to actually download)
            # download_path = dag.download(product, outputs_prefix=download_dir)
            # print(f"✓ Downloaded to: {download_path}")
            
            print("(Download commented out for demo)")
            print("Uncomment the download lines to actually download")
            
        else:
            print("No products found for download")
            
    except Exception as e:
        print(f"✗ Download failed: {e}")

# =============================================================================
# 6. ADVANCED PLUGIN CONFIGURATION
# =============================================================================

def create_advanced_opensearch_config():
    """Create advanced OpenSearch configuration with custom parameters"""
    
    config = {
        'cop_dataspace_advanced': {
            'priority': 1,
            'description': 'Advanced Copernicus Dataspace OpenSearch configuration',
            
            'search': {
                'plugin': 'QueryStringSearch',
                'api_endpoint': 'https://catalogue.dataspace.copernicus.eu/resto/api/collections/{collection}/search.json',
                
                # Advanced pagination
                'pagination': {
                    'next_page_query_obj': '{{"page": {page}, "maxRecords": {items_per_page}}}',
                    'total_items_nb_key_path': '$.properties.totalResults',
                    'max_items_per_page': 2000
                },
                
                # Custom query parameters
                'query_params': {
                    'format': 'json',
                    'sortParam': 'startDate',
                    'sortOrder': 'descending',
                    'status': 'all',
                    'dataset': 'ESA-DATASET'
                },
                
                # Metadata discovery
                'discover_metadata': {
                    'auto_discovery': True,
                    'metadata_pattern': 'https://catalogue.dataspace.copernicus.eu/resto/api/collections/{collection}/describe.xml'
                },
                
                # Advanced filtering
                'filter_overlap': 'intersects',
                'filter_date_overlap': 'intersects',
                
                # Custom headers
                'custom_headers': {
                    'User-Agent': 'EODAG-OpenSearch-Client/1.0',
                    'Accept': 'application/json'
                }
            },
            
            'download': {
                'plugin': 'HTTPDownload',
                'base_uri': 'https://zipper.dataspace.copernicus.eu/odata/v1',
                'extract': False,
                'archive_depth': 1,
                'timeout': 600,  # 10 minutes
                'chunk_size': 65536,  # 64KB chunks
                'max_retries': 3,
                'retry_delay': 5,
                'concurrent_downloads': 2
            },
            
            'auth': {
                'plugin': 'OAuth2ResourceOwnerPasswordCredentialsFlow',
                'token_provision': 'header',
                'auth_uri': 'https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token',
                'client_id': 'cdse-public',
                'token_exchange_params': {
                    'grant_type': 'password',
                    'client_id': 'cdse-public'
                },
                'credentials': {
                    'username': '${COPERNICUS_USERNAME}',
                    'password': '${COPERNICUS_PASSWORD}'
                },
                'token_refresh_margin': 300  # Refresh 5 minutes before expiry
            }
        }
    }
    
    return config

# =============================================================================
# 7. MAIN EXECUTION
# =============================================================================

def main():
    """Main function demonstrating OpenSearch plugins usage"""
    
    print("=== EODAG OpenSearch Plugins Demo ===\n")
    
    # Check credentials
    if not os.getenv('COPERNICUS_USERNAME') or not os.getenv('COPERNICUS_PASSWORD'):
        print("⚠️  Missing credentials!")
        print("Set environment variables:")
        print("  export COPERNICUS_USERNAME='your_username'")
        print("  export COPERNICUS_PASSWORD='your_password'")
        print("\nRegister at: https://dataspace.copernicus.eu/")
        return
    
    try:
        # Inspect available plugins
        inspect_plugins()
        
        # Debug provider configuration
        debug_provider_config()
        
        # Create and save configuration
        create_yaml_config()
        
        # Run search examples
        search_sentinel2_opensearch()
        search_sentinel1_opensearch()
        search_sentinel5p_opensearch()
        
        # Download example
        download_with_opensearch_plugins()
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

# =============================================================================
# PLUGIN ARCHITECTURE SUMMARY
# =============================================================================

"""
EODAG OPENSEARCH PLUGINS ARCHITECTURE:

1. SEARCH PLUGINS:
   - QueryStringSearch: OpenSearch/Elasticsearch compatible search
   - ODataV4Search: OData v4 protocol search
   - CSWSearch: Catalog Service for Web search
   - PostJsonSearch: JSON POST-based search
   - SentinelHubSearch: Sentinel Hub API search

2. DOWNLOAD PLUGINS:
   - HTTPDownload: Standard HTTP download
   - AwsDownload: AWS S3 download
   - HTTPSDownload: HTTPS download with SSL verification
   - SentinelHubDownload: Sentinel Hub download

3. AUTHENTICATION PLUGINS:
   - OAuth2AuthorizationCodeFlow: OAuth2 authorization code
   - OAuth2ResourceOwnerPasswordCredentialsFlow: OAuth2 password flow
   - HTTPHeaderAuth: HTTP header authentication
   - QueryStringAuth: Query string authentication
   - OAuth2ClientCredentialsFlow: OAuth2 client credentials

4. CONFIGURATION STRUCTURE:
   providers:
     provider_name:
       search:
         plugin: PluginName
         plugin_specific_config: ...
       download:
         plugin: PluginName  
         plugin_specific_config: ...
       auth:
         plugin: PluginName
         plugin_specific_config: ...
       products:
         product_type:
           collection: collection_name
           additional_params: ...

KEY OPENSEARCH PLUGIN FEATURES:
- Automatic pagination handling
- Metadata discovery from OpenSearch description documents
- Flexible query parameter mapping
- Support for spatial and temporal filtering
- Built-in retry mechanisms
- Concurrent download support
- Token refresh automation

COPERNICUS DATASPACE SPECIFICS:
- Uses QueryStringSearch plugin for OpenSearch API
- HTTPDownload plugin for OData v1 downloads
- OAuth2ResourceOwnerPasswordCredentialsFlow for authentication
- Collection-based product organization
- Automatic token management and refresh
"""