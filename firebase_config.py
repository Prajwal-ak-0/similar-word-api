import os
import firebase_admin
from firebase_admin import credentials, storage
from dotenv import load_dotenv

load_dotenv()

def initialize_firebase():
    cred_dict = {
        "type": os.getenv("FIREBASE_TYPE"),
        "project_id": os.getenv("FIREBASE_PROJECT_ID"),
        "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
        "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n"),
        "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
        "client_id": os.getenv("FIREBASE_CLIENT_ID"),
        "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
        "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
        "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
        "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL"),
        "universe_domain": os.getenv("FIREBASE_UNIVERSE_DOMAIN")
    }

    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(
        cred, {
            'storageBucket': os.getenv("FIREBASE_STORAGE_BUCKET")
        }
    )

    return storage.bucket()

async def download_file_from_firebase(bucket, file_path, local_path):
    # check if file already exists
    if not os.path.exists(local_path):
        blob = bucket.blob(file_path)
        print(f"Downloading {file_path}...")
        blob.download_to_filename(local_path)
        print('File downloaded successfully.')
    else:
        print(f"File {local_path} already exists.")