import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from controller import processCustomEncryption, processTotalEncryption, processPresetEncryption, processDecryption, getPresetWords
from settings_utils import loadSettings, refreshListbox, deleteSelectedWords, saveSettings

#Here are stored the UI's functions such as the menu, options, settings and etc.

# --- Micro Management Functions ---

#Cleans all widgets in window
def cleanMenu(root):

    try:
        for widget in root.winfo_children():
            widget.destroy()
    except Exception as e:
        raise RuntimeError("Error trying to clean the menu") from e

#Cleans window and shows the selected menu
def goBack(root, settings_data=None, fullscreen_var=None, return_function=None):
    if settings_data and fullscreen_var is not None:
        settings_data["fullscreen"] = fullscreen_var.get()
        saveSettings(settings_data)

    cleanMenu(root)
    #return_function can be a menu, for example return_function=showMainMenu() returns to the main menu
    if return_function:
        return_function(root)

# --- Main Menu ---

def showMainMenu(root):
    root.title("Safe Prompts")
    root.geometry("300x250")

    def on_encrypt():
        print("Encrypt clicked")
        showEncryptionMenu(root)

    def on_decrypt():
        #Since there is no decryption menu, I decided to simply execute the process directly from the user's interaction with the button
        print("Decrypt clicked")
        processDecryption(root)

    def on_settings():
        print("Settings clicked")
        showSettingsMenu(root)


    ttk.Label(root, text="Choose an option:", font=("Helvetica", 14)).pack(pady=20)

    ttk.Button(root, text="Encrypt Document", command=on_encrypt).pack(pady=5)
    ttk.Button(root, text="Decrypt Document", command=on_decrypt).pack(pady=5)
    ttk.Button(root, text="Settings", command=on_settings).pack(pady=5)

# --- Encryption Menu ---

def showEncryptionMenu(root):

    cleanMenu(root)

    def handle_total_encryption():
        print("Total Encryption Selected")
        processTotalEncryption(root)
    
    def handle_preset_encryption():
        print("Preset Encryption Selected")
        recommended_words = getPresetWords()
        processPresetEncryption(root,recommended_words)

    def handle_custom_encryption():
        print("Custom Encryption Selected")
        showCustomEncryptionMenu(root)

    ttk.Label(root, text="Choose encryption method:", font=("Helvetica", 14)).pack(pady=20)

    ttk.Button(root, text="Total Encryption", command=handle_total_encryption).pack(pady=5)
    ttk.Button(root, text="Preset Encryption", command=handle_preset_encryption).pack(pady=5)
    ttk.Button(root, text="Custom Encryption", command=handle_custom_encryption).pack(pady=5)
    ttk.Button(root, text="Back", command=lambda: goBack(root,settings_data=None,fullscreen_var=None,return_function=showMainMenu)).pack(side="right", padx=20)

# --- Custom Encryption Menu ---

def showCustomEncryptionMenu(root):
    cleanMenu(root)
    
    use_default = tk.BooleanVar()

    ttk.Label(root, text="Custom Encryption Setup", font=("Helvetica", 14)).pack(pady=5)

    # Unified input for words and optional substitutions
    ttk.Label(
        root,
        text='Insert the words to encrypt (e.g., "word1";"word2" or "word1":"sub1";"word2":"sub2"):'
    ).pack()
    word_input = tk.Text(root, height=6, width=50)
    word_input.pack(pady=5)

    ttk.Checkbutton(
        root,
        text="Include preset words in encryption (default set)",
        variable=use_default
    ).pack(pady=5)

    ttk.Button(
        root,
        text="Select file and proceed with Encryption",
        command=lambda: processCustomEncryption(
            root,
            word_input.get("1.0", "end").strip(),
            use_default.get()
        )
    ).pack(pady=5)
    ttk.Button(root, text="Back", command=lambda: goBack(root,settings_data=None,fullscreen_var=None,return_function=showEncryptionMenu)).pack(side="right", padx=20)

# --- Settings Menu ---

# Main Settings Menu
def showSettingsMenu(root):

    for widget in root.winfo_children():
        widget.destroy()

    settings_data = loadSettings()

    fullscreen_var = tk.BooleanVar(value=settings_data.get("fullscreen", False))
    fullscreen_check = ttk.Checkbutton(root, text="Open app in fullscreen mode", variable=fullscreen_var)
    fullscreen_check.pack(pady=5)


    ttk.Label(root, text="Settings", font=("Helvetica", 16)).pack(pady=10)
    ttk.Label(root, text="Recommended Encryption Expressions:").pack(pady=5)

    listbox = tk.Listbox(root, width=30, height=5)
    listbox.pack(pady=5)
    refreshListbox(listbox, settings_data)

    button_frame = ttk.Frame(root)
    button_frame.pack(pady=10)

    ttk.Button(button_frame, text="Add Preset Encryption Word", command=lambda: openAddWindow(root, settings_data, listbox)).pack(side="left", padx=2)
    ttk.Button(button_frame, text="Delete Selected", command=lambda: deleteSelectedWords(listbox, settings_data)).pack(side="left", padx=2)
    ttk.Button(button_frame, text="Back", command=lambda: goBack(root, settings_data, fullscreen_var, showMainMenu)).pack(side="left", padx=2)

#Opens the window for adding words to the Preset Encryption method
def openAddWindow(root, settings_data, listbox):
    add_window = tk.Toplevel(root)
    add_window.title("Add Preset Encryption Word")

    ttk.Label(add_window, text="Expression to encrypt:").pack(pady=5)
    expression_entry = ttk.Entry(add_window, width=40)
    expression_entry.pack()

    ttk.Label(add_window, text="Substitute word (optional):").pack(pady=5)
    substitute_entry = ttk.Entry(add_window, width=40)
    substitute_entry.pack()

    def addExpression():
        expr = expression_entry.get().strip()
        sub = substitute_entry.get().strip()

        if not expr:
            messagebox.showerror("Error", "Expression cannot be empty.")
            return

        preset_data = settings_data.get("preset", {})

        if expr in preset_data:
            messagebox.showwarning("Duplicate", "Expression already exists.")
            return

        preset_data[expr] = sub if sub else f"@@{len(preset_data):03d}"
        #Ensures structure update
        settings_data["preset"] = preset_data

        saveSettings(settings_data)
        refreshListbox(listbox, settings_data)
        add_window.destroy()

    ttk.Button(add_window, text="Add Expression", command=addExpression).pack(pady=10)
    ttk.Button(add_window, text="Cancel", command=add_window.destroy).pack()