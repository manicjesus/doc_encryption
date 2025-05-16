from cryptography.fernet import Fernet

#Here we manage functions that might be useful in testing

# --- Algorhytmns ---

def getFibonacciNumbers(n):
    """Generates a list of Fibonacci Numbers up to a max value of n (non-inclusive)"""
    if n <= 0:
        return []
    
    fib = [0, 1]
    while True:
        next_value = fib[-1] + fib[-2]
        if next_value >= n:
            break
        fib.append(next_value)
    return fib

# --- Micro Management Tools ---

def wasWordInadvertentlyRemoved(word, token_map, cypher):
    for sub, token in token_map.items():
        try:
            decrypted = cypher.decrypt(token.encode()).decode()
            if word in decrypted:
                return True
        except Exception as e:
            print(f"Error decyphering '{sub}': {e}")
    return False


