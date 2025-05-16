import json
import os
import tkinter as tk

#This file is exclusively for Settings functions

APP_DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'app_data')
SETTINGS_FILE = os.path.join(APP_DATA_DIR, 'settings.json')

# --- Settings ---

#Saves new data on settings.json
def saveSettings(data):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

#Loads settings.json
def loadSettings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
    else:
        data = {}

    #Garantees both of the keys exist in their default forms
    #isinstance() added to deal with tempering/corruption of the settings file
    if "fullscreen" not in data or not isinstance(data["fullscreen"],bool):
        data["fullscreen"] = False
    if "preset" not in data or not isinstance(data["preset"],dict):
        data["preset"] = {}

    return data

#Deletes the selected expressions from the listbox
def deleteSelectedWords(listbox, settings_data):
    selection = listbox.curselection()
    if not selection:
        return

    selected_line = listbox.get(selection[0])
    expr = selected_line.split(':')[0].strip().strip('"')

    preset = settings_data.get("preset", {})
    if expr in preset:
        del preset[expr]
        saveSettings(settings_data)  # salva o dicionário completo
        refreshListbox(listbox, settings_data)

#Refreshes listbox without needing to restart the app
def refreshListbox(listbox, data):
    listbox.delete(0, tk.END)
    preset = data.get("preset", {})

    if preset:
        for key, val in preset.items():
            listbox.insert(tk.END, f'"{key}" : "{val}"')
    else:
        print("Alert: No words on preset")

#Uses settings.json to decide if the app should be opened in fullscreen or not
def applyScreenSettings(root):
    settings = loadSettings()
    if settings.get("fullscreen", False):
        try:
            #Maximizes window
            root.state("zoomed")
        except:
            # Fallback for Linux/Mac
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            root.geometry(f"{screen_width}x{screen_height}+0+0")