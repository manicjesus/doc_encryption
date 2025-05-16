import tkinter as tk
from tkinter import messagebox

#This module is for notifications management
#it serves mostly as to avoid circular import errors and maintain scalability

# --- Notification Functions ---

#Simply shows a notification
def showNotification(title, message):
    messagebox.showinfo(title, message)
