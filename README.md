Local AI Chat
A desktop chat application for local LLMs
Description: Local AI Chat is a Python-based desktop application that enables real-time interaction with local language models using a modern CustomTkinter GUI. It supports two implementations: one leveraging the Ollama API with requests for streaming responses and another using the lmstudio library for simplified model integration. The app provides a seamless chat experience with context preservation, customizable response speed, and robust logging.
Key Features:

Real-time chat with local LLMs (e.g., Gemma, Mistral, LLaMA).
Streaming response display with word-by-word animation.
Persistent chat context for coherent dialogues.
Adjustable response speed via a slider.
Threaded processing to ensure a responsive GUI.
Chat history logging with file rotation.

Technologies:

Python, CustomTkinter, requests, lmstudio
Threading, JSON, Logging
Ollama API

Skills Demonstrated:

GUI development with CustomTkinter for a polished user interface.
API integration and streaming data processing with requests.
Multithreading to prevent UI freezes during AI responses.
Robust error handling and logging with file rotation.
Flexible architecture supporting multiple AI backends.

Installation:

Install dependencies: pip install customtkinter requests
For Ollama: Run ollama serve and pull desired models.
Run: python AI_chat_by_requests.py or python AI_chat_by_lmstudio.py

About Me: I'm a junior Python developer passionate about building interactive applications. After a six-month Python backend course, I created this project to showcase my skills in GUI programming, API integration, and AI interaction. I'm excited to contribute to open-source projects and grow as a developer.
