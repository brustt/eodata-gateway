import os
import json
from dotenv import load_dotenv
from eodag import EODataAccessGateway
from eodag import setup_logging

def create_opensearch_provider_config():
    """
    Create EODAG provider configuration using OpenSearch plugins for Copernicus Dataspace
    
    EODAG Plugin Architecture:
    - SearchPlugin: eodag.plugins.search.qssearch.QueryStringSearch (OpenSearch)
    - DownloadPlugin: eodag.plugins.download.http.HTTPDownload
    - AuthPlugin: eodag.plugins.authentication.oauth.KeycloakOIDCPasswordAuth
    """
    
    config = {
        'cop_dataspace_opensearch': {
            'priority': 1,
            'description': 'Copernicus Dataspace with OpenSearch API',
            
            # Search plugin configuration (OpenSearch)
            'search': {
                'plugin': 'QueryStringSearch',  # Built-in OpenSearch plugin
                'api_endpoint': 'https://catalogue.dataspace.copernicus.eu/resto/api/collections/{collection}/search.json',
                'need_auth': True,
                'timeout': 120,
                'ssl_verify': True,
                'pagination': {
                    'next_page_query_obj': '{"page": {page}, "maxRecords": {items_per_page}}',
                    'total_items_nb_key_path': '$.properties.totalResults',
                    'max_items_per_page': 1000
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
                    'format': 'json',
                    'startDate': '{startTimeFromAscendingNode}',
                    'completionDate': '{completionTimeFromAscendingNode}',
                    'productType': '{productType}',
                    'geometry': '{geometry}'
                },
                'results_entry': 'features',
                'metadata_mapping': {
                    # Basic metadata mapping for OpenSearch
                    'uid': '$.id',
                    'title': '$.properties.title',
                    'geometry': '$.geometry',
                    'startTimeFromAscendingNode': '$.properties.startDate',
                    'completionTimeFromAscendingNode': '$.properties.completionDate',
                    'productType': '$.properties.productType',
                    'downloadLink': '$.properties.services.download.url'
                }
            },
            
            # Download plugin configuration
            'download': {
                'plugin': 'HTTPDownload',
                'extract': True,
                'ssl_verify': True,
                'timeout': 300
            },
            
            # Authentication plugin configuration
            'auth': {
                'plugin': 'KeycloakOIDCPasswordAuth',
                'oidc_config_url': 'https://identity.dataspace.copernicus.eu/auth/realms/CDSE/.well-known/openid-configuration',
                'client_id': 'cdse-public',
                'token_provision': 'qs',
                'token_qs_key': 'token',
                'credentials': {
                    'username': os.environ.get('EODAG__COP_DATASPACE__AUTH__CREDENTIALS__USERNAME'),
                    'password': os.environ.get('EODAG__COP_DATASPACE__AUTH__CREDENTIALS__PASSWORD')
                }
            },
            
            # Product type mapping for Sentinel-2 products
            'products': {
                'S2_MSI_L1C': {
                    'collection': 'SENTINEL-2',
                    'productType': 'S2MSI1C'
                },
                'S2_MSI_L2A': {
                    'collection': 'SENTINEL-2',
                    'productType': 'S2MSI2A'
                }
            }
        }
    }
    
    return config


def test_opensearch_provider():
    """Test the OpenSearch provider configuration"""
    # Load environment variables from .env file
    load_dotenv()
    
    # Check if credentials are loaded
    username = os.environ.get('EODAG__COP_DATASPACE__AUTH__CREDENTIALS__USERNAME')
    password = os.environ.get('EODAG__COP_DATASPACE__AUTH__CREDENTIALS__PASSWORD')
    
    if not username or not password:
        print("ERROR: Credentials not found in environment variables")
        print("Make sure you have a .env file with the following variables:")
        print("EODAG__COP_DATASPACE__AUTH__CREDENTIALS__USERNAME=your_username")
        print("EODAG__COP_DATASPACE__AUTH__CREDENTIALS__PASSWORD=your_password")
        return
    
    # Create EODAG instance with our custom provider
    dag = EODataAccessGateway()
    
    # Register our custom provider
    provider_config = create_opensearch_provider_config()
    dag.update_providers_config(provider_config)
    
    # Set our provider as the default
    dag.set_preferred_provider('cop_dataspace_opensearch')
    
    # Print available providers to confirm registration
    print("Available providers:", dag.available_providers)
    
    # Simple search parameters
    search_params = {
        'productType': 'S2MSI1C',
        'startTimeFromAscendingNode': '2018-05-21',
        'completionTimeFromAscendingNode': '2018-05-25',
        'geometry': {
            'type': 'Polygon',
            'coordinates': [[[-105.0959, 36.5003], [-105.0959, 36.5590], 
                            [-104.9771, 36.5590], [-104.9771, 36.5003], [-105.0959, 36.5003]]]
        }
    }
    
    print("\nSearching for products with parameters:")
    print(json.dumps(search_params, indent=2))
    
    try:
        # Perform the search
        products = dag.search_all(**search_params)
        
        # Print results
        print(f"\nFound {len(products)} products:")
        for i, product in enumerate(products[:5]):
            print(f"\nProduct {i+1}:")
            print(f"  ID: {product.properties.get('id')}")
            print(f"  Title: {product.properties.get('title')}")
            print(f"  Date: {product.properties.get('startTimeFromAscendingNode')}")
            print(f"  Product Type: {product.properties.get('productType')}")
        
        if len(products) > 5:
            print(f"\n... and {len(products) - 5} more products")
            
    except Exception as e:
        print(f"\nError during search: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_opensearch_provider()
from eodag import EODataAccessGateway
from eodag import setup_logging
setup_logging(verbose=2)
dag = EODataAccessGateway()
dag.available_providers()
### Tests with Opensearch

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
config = create_opensearch_provider_config()
dag.update_providers_config(dict_conf=config)
dag.set_preferred_provider("cop_dataspace")

product_type = 'S2_MSI_L1C'
extent = {
    'lonmin': -105.095901,
    'lonmax': -104.977112,
    'latmin': 36.500253,
    'latmax': 36.559015
}

products_before = dag.search(
    productType=product_type,
    start='2018-05-21',
    end='2018-05-25',
    geom=extent,
)
products_before