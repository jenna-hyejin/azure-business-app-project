from flask import Flask, render_template, request, redirect, url_for
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError

app = Flask(__name__)

# Uses Azure Managed Identity when deployed to App Service
credential = DefaultAzureCredential()

KEY_VAULT_URL = "https://kv-business-app-dev.vault.azure.net/"
secret_client = SecretClient(
    vault_url=KEY_VAULT_URL,
    credential=credential
)

STORAGE_ACCOUNT_URL = "https://stbusinessappdev.blob.core.windows.net"
CONTAINER_NAME = "app-data"
BLOB_NAME = "business-note.txt"

blob_service_client = BlobServiceClient(
    account_url=STORAGE_ACCOUNT_URL,
    credential=credential
)

container_client = blob_service_client.get_container_client(CONTAINER_NAME)


@app.route("/")
def home():
    try:
        secret_client.get_secret("app-message")
        key_vault_status = "Loaded securely from Azure Key Vault"
    except Exception:
        key_vault_status = "Key Vault connection unavailable"

    try:
        blob_client = container_client.get_blob_client(BLOB_NAME)
        saved_note = blob_client.download_blob().readall().decode("utf-8")
    except ResourceNotFoundError:
        saved_note = "No note has been saved yet."
    except Exception:
        saved_note = "Blob Storage connection unavailable."

    return render_template(
        "index.html",
        key_vault_status=key_vault_status,
        saved_note=saved_note
    )


@app.route("/save", methods=["POST"])
def save_note():
    note = request.form.get("note", "").strip()

    if note:
        blob_client = container_client.get_blob_client(BLOB_NAME)
        blob_client.upload_blob(note, overwrite=True)

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)