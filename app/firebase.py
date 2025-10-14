from google.cloud import firestore
from google.oauth2 import service_account

CREDS = service_account.Credentials.from_service_account_file(
    "E:\\3. Estudis\\Treball de recerca\\TDR\\app\\assets\\trec-genispunti-firebase.json"
)

def updateDocument(document: str = "global_data", data: dict = {}, collection: str = "global_data"):
    db = firestore.Client(credentials=CREDS)
    doc_ref = db.collection(collection).document(document)
    doc_ref.update(data)

def getDocument(document: str = "global_data", collection: str = "global_data") -> dict:
    db = firestore.Client(credentials=CREDS)
    doc_ref = db.collection(collection).document(document)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    else:
        return {"ERROR": True}
    
def setDocument(document: str = "global_data", data: dict = {}, collection: str = "global_data"):
    db = firestore.Client(credentials=CREDS)
    doc_ref = db.collection(collection).document(document)
    doc_ref.set(data)

def getCollection(collection: str = "global_data"):
    db = firestore.Client(credentials=CREDS)
    doc_ref = db.collection(collection)
    return doc_ref.stream()