import customtkinter as ctk
import threading
import random
import time
import tkinter as tk
import lmstudio as lms
from datetime import datetime

# theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# settings
AVAILABLE_MODELS = ['llama-3.2-1b-instruct']
LOG_FILE = "chat_log.txt"

# Global flags and state
stop_generation = False
response_thread = None
chat_session = None
last_system_msg = None

def send_prompt():
    global stop_generation, chat_session, last_system_msg

    prompt = entry.get().strip()
    if not prompt:
        return

    model_name = selected_model.get()
    entry.delete(0, "end")

    # Disable input and buttons
    entry.configure(state="disabled")
    send_button.configure(state="disabled")
    stop_button.configure(state="normal")

    # Составляем новое системное сообщение
    system_msg = f"You are a helpful assistant using {model_name} model."

    # Если сессия не создана или модель/системное сообщение изменилось — создаём новую сессию
    if chat_session is None or last_system_msg != system_msg:
        chat_session = lms.Chat(system_msg)
        last_system_msg = system_msg

    chat_session.add_user_message(prompt)

    # Выводим запрос пользователя
    chat_history.configure(state="normal")
    chat_history.insert("end", f"\n🙋 You: {prompt}\n", "user")
    log_message("You", prompt)
    chat_history.insert("end", f"\n🤖 AI ({model_name}): ", "ai")
    chat_history.see("end")
    chat_history.configure(state="disabled")

    start_time = time.time()
    answer = ""

    try:
        # Создаём клиент для выбранной модели
        model = lms.llm(model_name)

        # Получаем ответ
        raw_response = model.respond(chat_session)

        # Приводим PredictionResult к строке
        if hasattr(raw_response, "text"):
            response_str = raw_response.text
        else:
            response_str = str(raw_response)

        # Сохраняем в сессию и лог
        chat_session.add_assistant_response(response_str)
        answer = response_str

        # Анимированный вывод по словам
        chat_history.configure(state="normal")
        for word in response_str.split():
            if stop_generation:
                break
            chat_history.insert("end", word + " ", "ai")
            chat_history.see("end")
            chat_history.update()
            time.sleep(random.uniform(0.01, 0.03))
        chat_history.configure(state="disabled")

    except Exception as e:
        answer = f"Exception: {e}"
        chat_history.configure(state="normal")
        chat_history.insert("end", answer, "ai")
        chat_history.configure(state="disabled")

    log_message("AI", answer)

    response_time = time.time() - start_time
    chat_history.configure(state="normal")
    chat_history.insert("end", f"\n[Response time: {response_time:.2f} seconds]\n", "info")
    chat_history.see("end")
    chat_history.configure(state="disabled")

    # Восстанавливаем интерфейс
    entry.configure(state="normal")
    send_button.configure(state="normal")
    stop_button.configure(state="disabled")
    entry.focus_set()

def clear_chat():
    global chat_session, last_system_msg
    chat_session = None
    last_system_msg = None
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
app.title("Local AI Chat")
app.geometry("900x650")

# Chat panel
chat_history = ctk.CTkTextbox(app, wrap="word", font=("SF Pro", 14), width=800, height=450)
chat_history.pack(pady=(20, 10), padx=20, fill="both", expand=True)
chat_history.configure(state="disabled")

# Bottom frame
frame_bottom = ctk.CTkFrame(app)
frame_bottom.pack(pady=10, padx=20, fill="x")

entry = ctk.CTkEntry(frame_bottom, font=("SF Pro", 20), width=400, placeholder_text="Type your message here...")
entry.pack(side="left", padx=(0, 10), fill="x", expand=True)
entry.bind("<Return>", lambda event: threaded_send_prompt())

send_button = ctk.CTkButton(frame_bottom, text="Send", command=threaded_send_prompt)
send_button.pack(side="left", padx=(0, 10))

clear_button = ctk.CTkButton(frame_bottom, text="Clear", command=clear_chat, fg_color="#e74c3c")
clear_button.pack(side="left", padx=(0, 10))

stop_button = ctk.CTkButton(frame_bottom, text="Stop", command=stop_ai_response, fg_color="#e74c3c", state="disabled")
stop_button.pack(side="left", padx=(0, 10))

selected_model = tk.StringVar(value=AVAILABLE_MODELS[0])
model_menu = ctk.CTkOptionMenu(frame_bottom, variable=selected_model, values=AVAILABLE_MODELS)
model_menu.pack(side="left", padx=(0, 10))

# Styling tags
chat_history.tag_config("user", foreground="#00BFFF")
chat_history.tag_config("ai", foreground="#7CFC00")
chat_history.tag_config("info", foreground="#AAAAAA")

# Start app
app.mainloop()
