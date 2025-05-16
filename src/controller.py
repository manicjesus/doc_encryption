import tkinter as tk
from tkinter import filedialog
import os
import re
from notifications import showNotification
from encryption_utils import createSubstitutionMap, encrypt_document, decrypt_document
from file_manager import readDocument, verifyDocument, verifyFolder, manageEncryptionFiles, loadDecryptionComponents, overwriteDocument, deleteAuxiliaryFile
from settings_utils import loadSettings

#Here we have the application controlers that do things such as process the actions from the encryption menus

# --- Process Utils ---

#Depending on the encryption/decryption method, this function will 
#either retrieve a document (for encryption) or return the necessary 
#components for decryption.
def getDocument(root,process=None):

    if process == 'encryption':
        #Encryption: Retrieve document and file path for encryption
        file_path = filedialog.askopenfilename(title="Select file to encrypt", filetypes=[("Text files", "*.txt")])
        if not file_path or not verifyDocument(file_path):
            showNotification("Error", "Invalid or no file selected.")
            return     
    elif process == 'decryption':
        # Decryption: Retrieve folder, token_map and key for decryption
        folder_path = filedialog.askdirectory(title="Select folder for decryption")
        folder_name = os.path.basename(folder_path)

        #In case of _number suffix in the end of the folder's name, we remove it to confirm the .txt file.
        base_name = re.sub(r'_\d+$', '', folder_name)

        #Builds the path towards the .txt
        file_path = os.path.join(folder_path, f"{base_name}.txt")
        print(f"folder name {folder_name}, base name {base_name}, folder path {folder_path}, file path {file_path}")
        if not os.path.isfile(file_path):
            print(f"Error: {file_path} doesn't exist.")
            showNotification("Error","Error: there's no valid file to decrypt, guarantee that there's a file with the same name as the folder and finished in .txt")
            return
        if not folder_path or not verifyFolder(folder_path):
            showNotification("Error", "Invalid or no folder selected.")
            return
        
        try:
            #loadDecryptionComponents [file_manager.py] loads the respective files necessary for decryption
            token_map, cypher, key = loadDecryptionComponents(folder_path)
        except ValueError as e:
            showNotification("Error", str(e))
            return
    try:
        document = readDocument(file_path)
    except ValueError as e:
        showNotification("Error",f"Error while reading document from file path '{file_path}'", str(e))
        return
    if process == 'encryption':
        return document, file_path        
    elif process == 'decryption':
        return document, file_path, folder_path, token_map, cypher, key
    else:
        showNotification("Failed","Something went wrong")
        print("Error on getDocument()")
        return

#As to simplify the code on the processing functions there's this function that checks if all encryption variables are set
#calls the folder creation process and notifies the user
def wrapUpEncryption(file_path=None,document=None,encrypted_document=None,token_map=None,cypher=None,key=None,encryption_method='total'):
    if encrypted_document and token_map and cypher:
        try:
            folder = manageEncryptionFiles(file_path,document,encrypted_document,token_map,key,encryption_method)
        except:
            print(f"Error while managing the encryption folder")
        
        showNotification("Success", f"Document encrypted and saved in:\n{folder}")
    else:
        showNotification("Failed","Something went wrong while encrypting the document")
    return

#Gets the words on the preset key of settings.json if there are any
def getPresetWords():
    if loadSettings().get('preset'):
        return loadSettings().get('preset')
    return None

# --- Process Encryption Requests ---

#Process Total Encryption Selection
def processTotalEncryption(root, encryption_method='total'):
    process = 'encryption'
    #Get document from User
    document, file_path = getDocument(root,process)
    #Encryption Algorhytmn
    encrypted_document, token_map, cypher, key = encrypt_document(document)
    #Wrap Up the process
    wrapUpEncryption(file_path,document,encrypted_document,token_map,cypher,key,encryption_method)
    return

#Process Preset/Recommended Encryption Selection
def processPresetEncryption(root,recommended_words=None,encryption_method='preset'):
    process = 'encryption'
    if recommended_words == None:
        showNotification("Error","The preset collection is empty: Please configure the collection on the Settings tab located on the Main Menu...")
        return
    
    wordsToEncrypt = recommended_words
    #Get document from User
    document, file_path = getDocument(root,process)
    #Encryption Algorhytmn
    encrypted_document, token_map, cypher, key = encrypt_document(document,encryption_method,wordsToEncrypt)
    #Wrap Up the process
    wrapUpEncryption(file_path,document,encrypted_document,token_map,cypher,key,encryption_method) 
    pass

#Process Custom Encryption Selection
def processCustomEncryption(root, input_substitution_words, use_default=False, recommended_words=None, encryption_method='custom'):
    #The substitution map is a reference to the function createSubstitutionMap from encryption_utils.py
    #It returns a map on the format: {'Generates': 'verb1', 'fernet key': 'object', 'Keep': 'verb2'}
    process = 'encryption'
    #Validate Input
    if not input_substitution_words:
        showNotification("Error", "Select at least one word to encrypt before continuing.")
        return

    custom_values = dict()
    substitution_pairs = input_substitution_words.split(";")
    for pairOfWords in substitution_pairs:
        if ":" in pairOfWords:
            word, sub = pairOfWords.split(":", 1)
            word = word.strip().strip('"')
            sub = sub.strip().strip('"')
            custom_values[word] = sub
        else:
            custom_values[pairOfWords] = ""
    #After evaluating every pair of words inputed for substitution we call the createSubstitutionMap()
    print(f"custom values: {custom_values}, input: {input_substitution_words}")
    custom_substitution_map = createSubstitutionMap(custom_values)

    wordsToEncrypt = [word for word in custom_substitution_map.keys()]

    if use_default == True:
        recommended_words = getPresetWords()

    #Get document from User
    document, file_path = getDocument(root,process)
    #Encryption Algorhytmn
    encrypted_document, token_map, cypher, key = encrypt_document(document,encryption_method,wordsToEncrypt,custom_substitution_map,recommended_words)
    #Wrap Up the process
    wrapUpEncryption(file_path,document,encrypted_document,token_map,cypher,key,encryption_method)
    return

# --- Process Decryption Requests ---

#Process Decryption
def processDecryption(root):
    process = 'decryption'

    #Get document from User
    encrypted_document, file_path, folder_path, token_map, cypher, key = getDocument(root,process)
    #Verify encryption method
     
    #Decryption
    decrypted_document = decrypt_document(encrypted_document, token_map, cypher)
    
    if decrypted_document:
        overwriteDocument(file_path,decrypted_document)
        deleteAuxiliaryFile(folder_path,"token_map.json")
        deleteAuxiliaryFile(folder_path,"key.key")
        showNotification("Success","Decryption Completed with Success!")
    else:
        showNotification("Failed","Decryption Incomplete")
        print(f"Decrypted Document is missing")
        return
    return