from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

AZURE_KEYVAULT_URL = 'https://hearthandkin.vault.azure.net/'
AZURE_BLOB_URL = 'https://hearthandkin.blob.core.windows.net/'
# Create an instance of the DefaultAzureCredential class to authenticate with Azure using managed identity
credential = DefaultAzureCredential()

# Initialize a connection to the Azure storage account
blob_service_client = BlobServiceClient(account_url=AZURE_BLOB_URL, credential=credential)
# Specifies the "public" directory in the Azure Blob Storage container
public_container_client = blob_service_client.get_container_client('public')

# Create an instance of the SecretClient class to interact with the Azure Key Vault
client = SecretClient(vault_url=AZURE_KEYVAULT_URL, credential=credential)

def store_public(remote_path: str, file: bytes | None = None, url: str | None = None) -> str:
    """
    Store a file in the public Azure Blob Storage container and return the URL to the stored file.
    The file can be either a bytes object or a URL.
    """

    blob_client = public_container_client.get_blob_client(blob=remote_path)
    if file:
        blob_client.upload_blob(file, overwrite=True)
    elif url:
        blob_client.upload_blob_from_url(url, overwrite=True)

    return blob_client.url


def get_secret(name: str) -> str | None:
    secret = client.get_secret(name)
    return secret.value if secret else None