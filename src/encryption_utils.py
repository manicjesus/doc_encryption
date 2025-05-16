from cryptography.fernet import Fernet
import re
import json
import os
from settings_utils import loadSettings
from file_manager import APP_DATA_DIR, BASE_DIR

#Here is were all the encryption happens, key generation, encryption and decryption are in this script.

# --- Customization ---

#This function has been replaced by addExpression() inside openAddWindow in ui.py
def updateRecommendedWords(words, path=None):
    if path is None:
        path = os.path.join(APP_DATA_DIR, "settings.json")
        
    settings = loadSettings(path)
    
    #Adds new words
    settings["recommended_words"] = words
    
    #Overwrites the file
    with open(path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4)

def addWordsToEncrypt(words):

    wordsToEncrypt = list()

    for word in words:
        if word not in wordsToEncrypt:
            wordsToEncrypt.append(word)

    return wordsToEncrypt

def createSubstitutionMap(custom_values=dict()):
    #This function returns a dict(), whose keys are the words to be encrypted and the values are the subsequent subs
    #Example: custom_value = {"hey":"word","ho":"anotherWord","let's":"word","go":"word"} will return {"hey":"word1","ho":"anotherWord","let's":"word2","go":"word3"}
    custom_substitution_map = dict()

    if not custom_values:
        print("Error: custom_substitution_map is Empty")
        return custom_substitution_map
    else: 
        counter = {}
        for word, sub in custom_values.items():
            #Here we check if the counter-like dict has any key equal to the substitute word being processed
            if sub not in counter:
                counter[sub] = 1
            else:
                counter[sub] += 1
            
            #After dealing with the counter we check how many iterations of the substitute word have been counted
            if list(custom_values.values()).count(sub) == 1:
                custom_substitution_map[word] = sub
            else:
                try:
                    custom_substitution_map[word] = f"{sub}{counter[sub]}"
                except KeyError:
                    raise f"Error: No sub called {sub} found in counter"
        return custom_substitution_map

# --- Key Management ---

def generate_key():
    return Fernet.generate_key()

# --- Encryption Function ---

def encrypt_document(document,encryption_method='total',wordsToEncrypt=None,custom_substitution_map=None,recommended_words=None):
    #Safety measure to avoid leaking
    if wordsToEncrypt is None:
        wordsToEncrypt = []

    #Here we create cypher, a Fernet class that is the algorhytmn used to encrypt/decrypt the document
    key = generate_key()
    cypher = Fernet(key)

    token_map = dict()
    encrypted_document = ''.join(caracter for caracter in document)

    #Here we make a substitution map that is to be updated with both the custom and recommended entries if they exist
    full_substitution_map = {}

    if isinstance(custom_substitution_map, dict):
        full_substitution_map.update(custom_substitution_map)
    if isinstance(recommended_words, dict):
        #If recommended_words exists and is dict() then we have to add the words in the list of words to encrypt
        if encryption_method == 'preset' or encryption_method == 'custom':
            try:
                wordsToEncrypt = wordsToEncrypt + addWordsToEncrypt(recommended_words.keys())
            except AttributeError:
                return "Error while adding recommended words into the list of words to encrypt"
            full_substitution_map.update(recommended_words)

    if encryption_method == 'total':
        #In case of total encryption, we'll encrypt the text as a whole
        encrypted_document = cypher.encrypt(document.encode()).decode()
        token_map['key'] = encrypted_document
    else:
        for i, word in enumerate(wordsToEncrypt):
            if not re.search(rf"{re.escape(word)}(?=\W|$)", document):
                print(f"Warning: Word '{word}' not in the given document, will be ignored.")
                continue

            encrypted_word = cypher.encrypt(word.encode()).decode()

            if word in full_substitution_map and full_substitution_map[word] != '':
                token = full_substitution_map[word]
            else:
                token = f"@@{i:03d}"
                print(f"Warning: Word '{word}' not found in substitution map, fallback to {token}")

            token_map[token] = encrypted_word
            encrypted_document = re.sub(re.escape(word), token, encrypted_document)

    return encrypted_document, token_map, cypher, key      
    
    
# --- Decryption Function ---

def decrypt_document(encrypted_document, token_map,cypher=None,encryption_method='total'):

    if token_map.get('encryption_method'):
        encryption_method = token_map['encryption_method']
        token_map.pop('encryption_method', None)
    else:
        print(f"Encryption method missing from token_map.json, assumed as total encryption")
    decrypted_document = ''.join(caracter for caracter in encrypted_document)

    if encryption_method == 'total':
        try:
            decrypted_document = cypher.decrypt(token_map['key']).decode()

        except KeyError:
            return "Error: cypher 'key' was not found - total_decryption error"
        
        except NameError:
            return "Error: token_map is not defined - decryption error"
        
        except AttributeError:
            return "Error: cypher is missing - decryption error"

        return decrypted_document
    else:
        for token in token_map:
            decrypted_word = cypher.decrypt(token_map[str(token)]).decode()
            decrypted_document = re.sub(token, decrypted_word, decrypted_document)
            
        return decrypted_document
    pass

# --- TESTS ---                               

#wordsTo=addWordsToEncrypt(["hey","ho"])
#print(wordsTo) #["hey","ho"]

#token_map, cypher = encrypt_document("hey ho les go ahsuduashdushduhsddushdaduhsadhus")
#print(f"token_map: {token_map}, encrypted_document: {encrypted_document}, cypher: {cypher}")
#decrypted=decrypt_document(token_map,cypher)
#print(decrypted)

#encryption_method = 'custom'
#text = "Generates a fresh fernet key. Keep this some place safe! If you lose it you'll no longer be able to decrypt messages"
#wordsToEncrypt = addWordsToEncrypt(["Generates","fernet key","safe!","palavra"])
#encrypted_document, token_map, cypher = encrypt_document(text,encryption_method,wordsToEncrypt)
#print(f"token_map: {token_map}, encrypted_document: {encrypted_document}, cypher: {cypher}")
#decrypted_document=decrypt_document(encrypted_document, token_map, cypher, encryption_method)
#print(f"decrypted_document:{decrypted_document}, encrypted_document:{encrypted_document}")


#encryption_method = 'custom'
#text = "Generates a fresh fernet key. Keep this some place safe! If you lose it you'll no longer be able to decrypt messages"
#wordsToEncrypt = addWordsToEncrypt(["Generates","fernet key","safe!","palavra"])
#custom_substitution_map = {"Generates":"verbo1","fernet key":"objetoChave"}
#encrypted_document, token_map, cypher = encrypt_document(text,encryption_method,wordsToEncrypt,custom_substitution_map)
#print(f"token_map: {token_map}, encrypted_document: {encrypted_document}, cypher: {cypher}")
#decrypted_document=decrypt_document(encrypted_document, token_map, cypher, encryption_method)
#print(f"decrypted_document:{decrypted_document}, encrypted_document:{encrypted_document}")


#encryption_method = 'custom'
#text = "Generates a fresh fernet key. Keep this some place safe! If you lose it you'll no longer be able to decrypt messages"
#wordsToEncrypt = addWordsToEncrypt(["Generates","fernet key","safe!","palavra","Keep"])
#custom_substitution_map = createSubstitutionMap({"Generates":"verbo","fernet key":"objetoChave","Keep":"verbo"})
#encrypted_document, token_map, cypher = encrypt_document(text,encryption_method,wordsToEncrypt,custom_substitution_map)
#print(f"token_map: {token_map}, encrypted_document: {encrypted_document}, cypher: {cypher}")
#decrypted_document=decrypt_document(encrypted_document, token_map, cypher, encryption_method)
#print(f"decrypted_document:{decrypted_document}, encrypted_document:{encrypted_document}")


#print(custom_substitution_map)