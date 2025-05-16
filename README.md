doc_encryption.py is a script that allows you to encrypt/decrypt documents locally, you may encrypt documents with three different methods:

    - Total Encryption: It generates just one token for all the document, encrypting the document as a whole;

    - Preset Encryption: It encrypts the pre-defined words that are defined by the user on the settings tab;
    
    - Custom Encryption: Here the user selects individually every word they might want to encrypt in the document (they are also able to check the "preset words" checkbox to encrypt both the selected and the preset words), every word/expression will get a token of it's own.

The script returns a folder named by the document and accompanied by a underscore '_' and a number IF AND ONLY IF there's another folder with the same name on the encrypted_documents folder. The folder returned containes the following files: 

    - A text file called nameOfDocument_encrypted.txt which contains the encrypted document;

    - A JSON file called token_map.json which contains the map of tokens for each word;

    - A .KEY file called key.key which contains the algorhytmn's document key.

THIS SCRIPT UTILIZES Fernet cryptography:
https://cryptography.io/en/latest/fernet/

WHAT FUTURE USE CASES COULD BE:
    - Ability to make an online account that stores global passwords for documents;
    - Having company-locked scripts that are configured for local use, having fixed preset words with admin-like access;