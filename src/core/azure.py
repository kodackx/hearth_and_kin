from azure.storage.blob import BlobServiceClient
import os

AZURE_CDN_URL = os.getenv('AZURE_CDN_URL')
AZURE_CONNECTION_STRING = os.getenv('AZURE_CONNECTION_STRING')


def store_public(remote_path: str, file: bytes | None = None, url: str | None = None) -> str:
    # Initialize a connection to the Azure storage account
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
    # Get a client to interact with the specified container
    private_container_client = blob_service_client.get_container_client('private')
    public_container_client = blob_service_client.get_container_client('public')
    blob_client = public_container_client.get_blob_client(blob=remote_path)
    if file:
        blob_client.upload_blob(file, overwrite=True)
    elif url:
        blob_client.upload_blob_from_url(url, overwrite=True)

    return blob_client.url
