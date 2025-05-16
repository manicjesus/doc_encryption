import os 
import json
from cryptography.fernet import Fernet
from notifications import showNotification

#Here I stored all the file management functions

# --- Encrypted Documents Directory ---

#Current Directory
main_dir = os.path.join(os.path.dirname(__file__),'..')
APP_DATA_DIR = os.path.join(main_dir, 'app_data')
BASE_DIR = os.path.join(APP_DATA_DIR, "encrypted_documents")

#Creates the encrypted_documents folder
try:
    os.makedirs(BASE_DIR, exist_ok=True)
except OSError as e:
    print(f"Error creating folder: {e}")


# --- Read Document To Be Encrypted ---

#Checks if the document exists and is valid for encryption
def verifyDocument(path):
    return os.path.isfile(path) and path.endswith(".txt")

#Reads the document
def readDocument(path):
    if verifyDocument(path):
        with open(path, "r", encoding="utf-8") as document:
            return document.read()
    else:
        raise ValueError(f"Error: invalid path - {path}")

# --- Modify Files ---

#Overwrites a document
def overwriteDocument(path, content):
    with open(path, "w", encoding="utf-8") as document:
        document.write(content)

#Deletes the auxiliary file (to delete token_map and key files after decryption)
def deleteAuxiliaryFile(folder_path, file_to_delete):
    file_path = os.path.join(folder_path, file_to_delete)

    if os.path.isfile(file_path):
        try:
            os.remove(file_path)
            print(f"Deleted: {file_path}")
        except OSError as e:
            print(f"Error deleting file: {e}")
    else:
        print(f"File not found: {file_path}")


# --- Document Specific Folder Creation ---

#Verify if directory with the same name exists
def verifyFolder(path):
    return os.path.isdir(path)

#Creates specific folder for the document
def createDocumentFolder(file_path, BASE_DIR):

    document_name = os.path.splitext(os.path.basename(file_path))[0]
    folder = os.path.join(BASE_DIR, document_name)
    #If there are other folders with the same name, the new folder is called by it's name followed by _ and the number of the iteration
    #If there is one other folder with the same name, the new will be called name_1
    if verifyFolder(folder):
        count = 1
        while True:
            new_name = f"{document_name}_{count if count > 0 else ''}"
            folder = os.path.join(BASE_DIR, new_name)
            if not verifyFolder(folder):
                break
            count += 1

    os.makedirs(folder)
    return folder    

# Save token_map.json file in folder
def saveTokenMap(folder_path, token_map, encryption_method):
    #Adds the method of encryption on the key --- makes it easier to manage decryption later
    token_map_with_method = {
        "encryption_method": encryption_method,
        **token_map
    }

    with open(os.path.join(folder_path, "token_map.json"), "w", encoding="utf-8") as file:
        json.dump(token_map_with_method, file, indent=2)


#Save cypher_key.key file in folder
def saveKey(folder_path, key):
    key = key.decode()
    #Extracts and converts the bytes to string
    print(f"Folder Path: {folder_path}, Key str:{key}")
    with open(os.path.join(folder_path, "key.key"), "w", encoding="utf-8") as file:
        file.write(key)

#Moves document to a folder
def moveDocumentToFolder(origin, destiny):
    if not os.path.exists(origin):
        os.makedirs(origin)
        print(f"Origin path not found - Created New Path: {origin}")

    document = os.path.basename(origin)
    new_path = os.path.join(destiny, document)

    os.rename(origin, new_path)

#Creates a folder with the documents name, saves on it the token_map.json, key.key, overwrites the document with it's encryption and moves it to the respective folder
def manageEncryptionFiles(file_path,document,encrypted_document,token_map,key, encryption_method):
    try:
        print(file_path)
        folder = createDocumentFolder(file_path,BASE_DIR)
        print(folder)
    except:
        showNotification("Failed","Something went wrong while encrypting the document")
        print(f"Error creating the document's '{document}' encryption folder")
        return
        
    try:
        saveTokenMap(folder, token_map, encryption_method)
    except:
        showNotification("Failed","Something went wrong while encrypting the document")
        print(f"Error saving the token_map '{token_map} on folder '{folder}")
        return
        
    try:
        saveKey(folder, key)
    except:
        showNotification("Failed","Something went wrong while encrypting the document")
        print(f"Error saving the key '{key}' on folder '{folder}'")
        return
        
    try:
        overwriteDocument(file_path, encrypted_document)
    except:
        showNotification("Failed","Something went wrong while encrypting the document")
        print(f"Error while overwriting the original document '{document}' with the encrypted content '{encrypted_document}'")
        
    try:
        moveDocumentToFolder(file_path, folder)
    except:
        showNotification("Failed","Something went wrong while encrypting the document")
        print(f"Error while moviment the overwritten file '{document}' onto to the new folder '{folder}'")
    return folder

#Loads token_map.json and key.key from selected folder_path
def loadDecryptionComponents(folder_path):
    token_map_path = os.path.join(folder_path, "token_map.json")
    key_path = os.path.join(folder_path, "key.key")

    if not os.path.exists(token_map_path):
        raise ValueError("token_map.json not found in selected folder.")
    
    if not os.path.exists(key_path):
        raise ValueError("key.key not found in selected folder.")

    #Loads the token_map
    with open(token_map_path, "r", encoding="utf-8") as f:
        token_map = json.load(f)

    #Loads the key
    with open(key_path, "r", encoding="utf-8") as f:
        key_str = f.read().strip()
        key = key_str.encode()

    cypher = Fernet(key)
    return token_map, cypher, key

#path = os.path.join(main_dir, "docExample.txt")
#print(readDocument(path))
#overwriteDocument(path,"asdasd")
#print(readDocument(path))
#folder_path = createDocumentFolder("docExample", BASE_DIR)
#print("Caminho da pasta criada:", folder_path)
#moveDocumentToFolder(path,folder_path)
#print("Caminho da pasta criada:", folder_path)

