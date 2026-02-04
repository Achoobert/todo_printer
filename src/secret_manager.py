import requests
import os

def get_key(label):
   vault_token = os.environ.get("VAULT_TOKEN") # Get from env or default
   vault_location = os.environ.get("LOCATION", "namespace/cubbyhole/secrets") # Get from env or default
   vault_addr = "http://127.0.0.1:8200"
   url = f"{vault_addr}/v1/{vault_location}"
   headers = {"X-Vault-Token": vault_token}

   try:
      response = requests.get(url, headers=headers)
      response.raise_for_status()  # Raise an exception for HTTP errors
      data = response.json()
      # Assuming the key is always under 'a' in the data payload based on the example
      return data["data"].get(f"{label}", None)
   except requests.exceptions.RequestException as e:
      print(f"Error fetching key for {label}: {e}")
      return None
