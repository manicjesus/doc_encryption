import sys
import os
import unittest
import re
from cryptography.fernet import Fernet
from test_utils import getFibonacciNumbers, wasWordInadvertentlyRemoved

#Adds the doc_encryption folder onto the module searching path
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
sys.path.append(src_path)

from encryption_utils import encrypt_document, decrypt_document # type: ignore

class TestEncryptionUtils(unittest.TestCase):
    
    total_tests = 0
    counter = 0

    @classmethod
    def setUpClass(cls):
        cls.total_tests = 7

    def setUp(self):
        # Corre antes de cada teste
        self.cypher = Fernet(Fernet.generate_key())
        self.token_map = {}
        self.text = ""
        self.wordsToEncrypt = []
        self.method = ""
        self.custom_substitution_map = {}

    def tearDown(self):
        TestEncryptionUtils.counter += 1
        print(f"✅ Test {TestEncryptionUtils.counter} of {TestEncryptionUtils.total_tests} concluded")
        
    # --- TEST IF TEXT != ENCRYPTED_TEXT ---

    #TOTAL ENCRYPTION
    def test_total_encryption_returns_encrypted_text(self):

        #Arrange test
        text = "This is a simple test for total encryption, let's check if it can encrypt the variable text despite the caracter's such as !#$%&/()=?{} or the numbers 121212124435"
        method = 'total'

        #Trial
        encrypted_text, token_map, cypher, key = encrypt_document(text,encryption_method=method)

        #Assert
        self.assertNotEqual(encrypted_text,text)
        self.assertIn("key", token_map)
        self.assertTrue(isinstance(encrypted_text, str))
        print(f"Total Encryption Test returned the encrypted text") 

    #PRESET ENCRYPTION
    def test_preset_encryption_returns_encrypted_text(self):

        #Arrange test
        text = "This is a simple test for preset encryption, let's check if it can encrypt only the preset words in the variable text despite the caracter's such as !#$%&/()=?{} or the numbers 121212124435"
        method = 'preset'
        recommended_words = {"test":"sub1","let's":"sub2","!#":"sub3","wordNotInText":"sub4"}

        #Trial
        encrypted_text, token_map, cypher, key = encrypt_document(text,encryption_method=method,recommended_words=recommended_words)

        #Assert
        self.assertNotEqual(encrypted_text,text)
        self.assertTrue(isinstance(encrypted_text, str))
        print(f"Preset Encryption Test returned the encrypted text") 

    #CUSTOM ENCRYPTION
    def test_custom_encryption_returns_encrypted_text(self):

        #Arrange test
        text = "This is a simple test for preset encryption, let's check if it can encrypt only the preset words in the variable text despite the caracter's such as !#$%&/()=?{} or the numbers 121212124435"
        method = 'custom'
        wordsToEncrypt = ["test","let's","!#","wordNotInText"]
        custom_substitution_map = {"test":"sub1","let's":"sub2","!#":"sub3","wordNotInText":"sub4"}

        #Trial
        encrypted_text, token_map, cypher, key = encrypt_document(text,encryption_method=method,wordsToEncrypt=wordsToEncrypt,custom_substitution_map=custom_substitution_map)

        #Assert
        self.assertNotEqual(encrypted_text,text)
        self.assertTrue(isinstance(encrypted_text, str))
        print(f"Custom Encryption Test returned the encrypted text") 

    #Tests if the words being encrypted are right
    def test_selection_of_words_to_encrypt_with_preset(self):

        #Arrange test
        text = "The crux of each test is a call to assertEqual() to check for an expected result; assertTrue() or assertFalse() to verify a condition; or assertRaises() to verify that a specific exception gets raised. These methods are used instead of the assert statement so the test runner can accumulate all test results and produce a report." 
        method = 'preset'
        wordsInText = text.split(" ")

        #Here we just choose the encryption words from the text according to the fibonacci sequence
        #it serves only to create a bit more of randomness in the testing
        fib_index = getFibonacciNumbers(len(wordsInText))
        wordsToEncrypt = [wordsInText[i] for i in fib_index if i < len(wordsInText)]
        recommended_words = {i: f"sub{idx}" for idx, i in enumerate(wordsToEncrypt)}

        #Trial
        encrypted_document, token_map, cypher, key = encrypt_document(text,encryption_method=method,recommended_words=recommended_words)

        #Assert
        #Words that should've been encrypted
        expected_encrypted_words = [word for word in recommended_words.keys()]

        #Words that shouldn't have been encrypted
        not_expected = [word for word in set(wordsInText) if word not in expected_encrypted_words]
        #print(f"WordsToEncrypt: {wordsToEncrypt}, Expected: {expected_encrypted_words}, Not Expected:{not_expected}")
        #print(f"THIS IS THE TOKEN MAP: {token_map}")

        for word in expected_encrypted_words:
            self.assertNotIn(word, encrypted_document, f"'{word}' should've been encrypted...")

        for word in not_expected:
            self.assertFalse(
                wasWordInadvertentlyRemoved(word, token_map, cypher),
                f"'{word}' shouldn't have been encrypted"
            )

        print(f"Preset Encryption Test returned the correct encryptions") 

    #DECRYPTION OVER TOTAL ENCRYPTION
    def test_if_decryption_returns_the_same_text_after_total_encryption(self):
        
        #Arrange tests
        text = "Usar listas ou dicionários como valor padrão em funções pode causar comportamentos inesperados, porque o valor default é compartilhado entre chamadas da função."
        method = 'total'
        encrypted_text, token_map, cypher, key = encrypt_document(text,method)

        #Trial
        decrypted_text = decrypt_document(encrypted_text,token_map,cypher)

        #Assert
        self.assertEqual(
            decrypted_text,
            text,
            f"Decrypted Text '{decrypted_text}' different from original text '{text}'")
        print(f"Decryption over TOTAL encryption returned same text as expected") 

    #DECRYPTION OVER PRESET ENCRYPTION
    def test_decryption_after_preset_encryption(self):

        #Arrange tests
        text = "Usar listas ou dicionários como valor padrão em funções pode causar comportamentos inesperados, porque o valor default é compartilhado entre chamadas da função."
        method = 'preset'
        wordsToEncrypt = ["Usar","dicionários","inesperados","função."]
        recommended_words = {"Usar":"sub1","dicionários":"sub2","inesperados":"blablabla","função.":"sub4"}
        encrypted_text, token_map, cypher, key = encrypt_document(text,encryption_method=method,wordsToEncrypt=wordsToEncrypt,recommended_words=recommended_words)
        if not token_map.get('encryption_method'):
            token_map['encryption_method'] = 'preset'

        #Trial
        decrypted_text = decrypt_document(encrypted_text,token_map,cypher,method)

        #Assert
        self.assertEqual(
            decrypted_text,
            text,
            f"Decrypted Text '{decrypted_text}' different from original text '{text}'")
        print(f"Decryption over PRESET encryption returned same text as expected") 

    #DECRYPTION OVER CUSTOM ENCRYPTION
    def test_decryption_after_custom_encryption(self):
        
        #Arrange tests
        text = "Usar listas ou dicionários como valor padrão em funções pode causar comportamentos inesperados, porque o valor default é compartilhado entre chamadas da função."
        method = 'custom'
        wordsToEncrypt = ["Usar","dicionários","inesperados","função."]
        custom_substitution_map = {"Usar":"sub1","dicionários":"sub2","inesperados":"blablabla","função.":"sub4"}
        encrypted_text, token_map, cypher, key = encrypt_document(text,encryption_method=method,wordsToEncrypt=wordsToEncrypt,custom_substitution_map=custom_substitution_map)
        if not token_map.get('encryption_method'):
            token_map['encryption_method'] = 'custom'

        #Trial
        decrypted_text = decrypt_document(encrypted_text,token_map,cypher,method)

        #Assert
        self.assertEqual(
            decrypted_text,
            text,
            f"Decrypted Text '{decrypted_text}' different from original text '{text}'")
        print(f"Decryption over CUSTOM encryption returned same text as expected") 

if __name__ == "__main__":
    unittest.main()