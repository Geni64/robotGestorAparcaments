from google.cloud import firestore
from google.oauth2 import service_account

CREDS = service_account.Credentials.from_service_account_file(
    "E:\\3. Estudis\\Treball de recerca\\TDR\\simulation\\assets\\trec-genispunti-firebase.json"
)

def updateDocument(document: str = "global_data", data: dict = {}):
    db = firestore.Client(credentials=CREDS)
    doc_ref = db.collection("global_data").document(document)
    doc_ref.update(data)

def getDocument(document: str = "global_data") -> dict:
    db = firestore.Client(credentials=CREDS)
    doc_ref = db.collection("global_data").document(document)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    else:
        return {"ERROR": True}
    
def setDocument(document: str = "global_data", data: dict = {}):
    db = firestore.Client(credentials=CREDS)
    doc_ref = db.collection("global_data").document(document)
    doc_ref.set(data)