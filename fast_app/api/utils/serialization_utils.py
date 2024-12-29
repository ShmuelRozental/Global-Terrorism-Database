from bson import ObjectId
import numpy as np

def serialize_doc(doc):
    if isinstance(doc, ObjectId):
        return str(doc)
    elif isinstance(doc, dict):
        return {key: serialize_doc(value) for key, value in doc.items()}
    elif isinstance(doc, list):
        return [serialize_doc(item) for item in doc]
    else:
        return doc



def convert_to_int(obj):
    if isinstance(obj, np.int64):  
        return int(obj)
    elif isinstance(obj, dict):  
        return {key: convert_to_int(value) for key, value in obj.items()}
    elif isinstance(obj, list):  
        return [convert_to_int(item) for item in obj]
    return obj  