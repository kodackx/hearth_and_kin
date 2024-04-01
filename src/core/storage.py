from azure.storage.blob import BlobServiceClient
import os

AZURE_CDN_URL = os.getenv('AZURE_CDN_URL')
AZURE_CONNECTION_STRING = os.getenv('AZURE_CONNECTION_STRING')
assert AZURE_CONNECTION_STRING, 'AZURE_CONNECTION_STRING env not found'

def store_public(remote_path: str, file: bytes | None = None, url: str | None = None) -> str:
    """
    Store a file in the public Azure Blob Storage container and return the URL to the stored file.
    The file can be either a bytes object or a URL.
    """
    # Initialize a connection to the Azure storage account
    blob_service_client = BlobServiceClient.from_connection_string(str(AZURE_CONNECTION_STRING))
    
    # Specifies the "public" directory in the Azure Blob Storage container
    public_container_client = blob_service_client.get_container_client('public')
    blob_client = public_container_client.get_blob_client(blob=remote_path)
    if file:
        blob_client.upload_blob(file, overwrite=True)
    elif url:
        blob_client.upload_blob_from_url(url, overwrite=True)

    return blob_client.url