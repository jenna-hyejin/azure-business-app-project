from flask import Flask, render_template
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

app = Flask(__name__)

KEY_VAULT_URL = "https://kv-business-app-dev.vault.azure.net/"

credential = DefaultAzureCredential()

secret_client = SecretClient(
    vault_url=KEY_VAULT_URL,
    credential=credential
)

@app.route("/")
def home():
    try:
        secret = secret_client.get_secret("app-message")
        message = secret.value
    except Exception:
        message = "Key Vault secret could not be loaded."

    return render_template(
        "index.html",
        message=message
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)