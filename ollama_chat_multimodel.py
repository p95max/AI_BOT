import customtkinter as ctk
import requests
import time
from datetime import datetime
import json

# theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# settings
OLLAMA_URL = 'http://localhost:11434/api/generate'
AVAILABLE_MODELS = ['gemma:2b', 'mistral', 'cogito:3b',]
LOG_FILE = "chat_log.txt"

# Send answer
def send_prompt():
    prompt = entry.get()
    if not prompt.strip():
        return

    model = selected_model.get()

    # Show user input
    chat_history.configure(state="normal")
    chat_history.insert("end", f"\nYou: {prompt}\n", "user")
    log_message("You", prompt)
    chat_history.insert("end", f"AI ({model}): Thinking...\n", "ai")
    chat_history.see("end")
    chat_history.configure(state="disabled")
    entry.delete(0, "end")

    # Start timing
    start_time = time.time()

    # Request to model
    try:
        response = requests.post(OLLAMA_URL, json={
            'model': model,
            'prompt': prompt,
            'stream': False
        })
        if response.status_code == 200:
            answer = response.json().get('response', 'No response.')
        else:
            answer = f"Error: {response.status_code}"
    except Exception as e:
        answer = f"Exception: {e}"

    log_message("AI", answer)

    # End timing
    end_time = time.time()
    response_time = end_time - start_time

    # Display answer + response time

    chat_history.configure(state="normal")
    chat_history.insert("end", f"{answer}\n", "ai")
    chat_history.insert("end", f"[Response time: {response_time:.2f} seconds]\n", "info")
    chat_history.see("end")
    chat_history.configure(state="disabled")

# Clear chat
def clear_chat():
    chat_history.configure(state="normal")
    chat_history.delete("1.0", "end")
    chat_history.configure(state="disabled")

def log_message(role, message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {role}: {message.strip()}\n")

# Main window
app = ctk.CTk()
app.title("Local AI Chat")
app.geometry("900x650")

# Chat panel
chat_history = ctk.CTkTextbox(app, wrap="word", font=("SF Pro", 14), width=800, height=450)
chat_history.pack(pady=(20, 10), padx=20, fill="both", expand=True)
chat_history.configure(state="disabled")

# Main window visible settings
frame_bottom = ctk.CTkFrame(app)
frame_bottom.pack(pady=10, padx=20, fill="x")

entry = ctk.CTkEntry(frame_bottom, font=("SF Pro", 20), width=400, placeholder_text="Type your message here...")
entry.pack(side="left", padx=(0, 10), fill="x", expand=True)
entry.bind("<Return>", lambda event: send_prompt())

send_button = ctk.CTkButton(frame_bottom, text="Send", command=send_prompt)
send_button.pack(side="left", padx=(0, 10))

clear_button = ctk.CTkButton(frame_bottom, text="Clear", command=clear_chat, fg_color="#e74c3c")
clear_button.pack(side="left", padx=(0, 10))

selected_model = ctk.StringVar(value=AVAILABLE_MODELS[0])
model_menu = ctk.CTkOptionMenu(frame_bottom, variable=selected_model, values=AVAILABLE_MODELS)
model_menu.pack(side="left", padx=(0, 10))

# Add tag for response time text (only color)
chat_history.tag_config("info", foreground="#AAAAAA")

# Launch app
app.mainloop()
