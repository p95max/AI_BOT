import customtkinter as ctk
import requests
import time
from datetime import datetime
import threading
import json
import markdown
import random

# theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# settings
OLLAMA_URL = 'http://localhost:11434/api/generate'
MODEL_NAME = 'gemma:2b'
LOG_FILE = "chat_log(gemma).txt"

# Global flags
stop_generation = False
response_thread = None

def send_prompt():
    global stop_generation

    prompt = entry.get()
    if not prompt.strip():
        return

    saved_prompt = prompt
    entry.delete(0, "end")

    # Disable input and buttons
    entry.configure(state="disabled")
    send_button.configure(state="disabled")
    stop_button.configure(state="normal")

    # Show user input
    chat_history.configure(state="normal")
    chat_history.insert("end", f"\nYou: {saved_prompt}\n", "user")
    log_message("You", saved_prompt)
    chat_history.insert("end", "AI: ", "ai")
    chat_history.see("end")
    chat_history.configure(state="disabled")

    start_time = time.time()
    answer = ""

    try:
        with requests.post(OLLAMA_URL, json={
            'model': MODEL_NAME,
            'prompt': saved_prompt,
            'stream': True
        }, stream=True) as response:
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line and not stop_generation:
                        try:
                            data = json.loads(line.decode("utf-8").lstrip("data: ").strip())
                            token = data.get("response", "")
                        except Exception:
                            token = ""
                        if token:
                            answer += token
                            chat_history.configure(state="normal")
                            for char in token:
                                chat_history.insert("end", char, "ai")
                                chat_history.see("end")
                                chat_history.update()
                                time.sleep(random.uniform(0.005, 0.02))  # случайная скорость
                            chat_history.configure(state="disabled")
                    if stop_generation:
                        break
            else:
                answer = f"\nError: {response.status_code}"
                chat_history.configure(state="normal")
                chat_history.insert("end", answer, "ai")
                chat_history.configure(state="disabled")
    except Exception as e:
        answer = f"\nException: {e}"
        chat_history.configure(state="normal")
        chat_history.insert("end", answer, "ai")
        chat_history.configure(state="disabled")

    log_message("AI", answer)

    response_time = time.time() - start_time
    chat_history.configure(state="normal")
    chat_history.insert("end", f"\n[Response time: {response_time:.2f} seconds]\n", "info")
    chat_history.see("end")
    chat_history.configure(state="disabled")

    # Re-enable input
    entry.configure(state="normal")
    send_button.configure(state="normal")
    stop_button.configure(state="disabled")
    entry.focus_set()

def clear_chat():
    chat_history.configure(state="normal")
    chat_history.delete("1.0", "end")
    chat_history.configure(state="disabled")

def log_message(role, message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {role}: {message.strip()}\n")

def threaded_send_prompt():
    global stop_generation, response_thread
    stop_generation = False
    response_thread = threading.Thread(target=send_prompt)
    response_thread.start()

def stop_ai_response():
    global stop_generation
    stop_generation = True
    stop_button.configure(state="disabled")

# Main window
app = ctk.CTk()
app.title("Local AI Chat 'Gemma'")
app.geometry("900x650")

chat_history = ctk.CTkTextbox(app, wrap="word", font=("SF Pro", 20), width=800, height=450)
chat_history.pack(pady=(20, 10), padx=20, fill="both", expand=True)
chat_history.configure(state="disabled")

frame_bottom = ctk.CTkFrame(app)
frame_bottom.pack(pady=10, padx=20, fill="x")

entry = ctk.CTkEntry(frame_bottom, font=("SF Pro", 14), width=400, placeholder_text="Type your message here...")
entry.pack(side="left", padx=(0, 10), fill="x", expand=True)
entry.bind("<Return>", lambda event: threaded_send_prompt())

send_button = ctk.CTkButton(frame_bottom, text="Send", command=threaded_send_prompt)
send_button.pack(side="left", padx=(0, 10))

clear_button = ctk.CTkButton(frame_bottom, text="Clear", command=clear_chat, fg_color="#e74c3c")
clear_button.pack(side="left", padx=(0, 10))

stop_button = ctk.CTkButton(frame_bottom, text="Stop", command=stop_ai_response, fg_color="#e74c3c", state="disabled")
stop_button.pack(side="left", padx=(0, 10))

chat_history.tag_config("user", foreground="#00BFFF")
chat_history.tag_config("ai", foreground="#7CFC00")
chat_history.tag_config("info", foreground="#AAAAAA")

app.mainloop()
