import os
import subprocess
import speech_recognition as sr
import pyttsx3
import requests
import re
import logging

# Setup Groq API
GROQ_API_KEY = "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"
GROQ_MODEL = "gemma2-9b-it"

# Initialize TTS
engine = pyttsx3.init()

# Set up logging with UTF-8 encoding to avoid issues with Unicode
logging.basicConfig(filename="assistant.log", level=logging.DEBUG, format='%(asctime)s - %(message)s', encoding='utf-8')

def speak(text):
    print("Assistant:", text)
    engine.say(text)
    engine.runAndWait()

# Listen to mic
def listen(language="en-US"):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source)
        try:
            audio = r.listen(source, timeout=5)
            recognized_text = r.recognize_google(audio, language=language)
            print(f"You said: {recognized_text}")
            return recognized_text
        except sr.WaitTimeoutError:
            speak("Sorry, I didn't hear anything. Please try again.")
            return ""
        except sr.UnknownValueError:
            speak("Sorry, I didn't understand that.")
            return ""
        except sr.RequestError:
            speak("Speech service is down.")
            return ""

def log_command(command_type, command):
    logging.info(f"{command_type}: {command}")

def log_user_input(user_input):
    try:
        with open("user_input_log.txt", "a", encoding='utf-8') as log_file:
            log_file.write(f"{user_input}\n")
    except Exception as e:
        logging.error(f"Failed to log user input: {e}")

# Check for dangerous commands
def is_restricted(cmd):
    restricted_keywords = ['del', 'erase', 'rm', 'format', 'shutdown', 'uninstall', 'regedit', 'taskkill', 'poweroff']
    for word in restricted_keywords:
        if word in cmd.lower():
            return True
    return False

# Handle built-in commands
def handle_basic(user_input):
    msg = user_input.lower()
    if "hello" in msg:
        speak("Hello! I'm your assistant.")
        return True
    elif "help" in msg:
        speak("You can ask me to open apps, calculate math, or run commands.")
        return True
    elif "your name" in msg:
        speak("I'm your smart assistant, powered by Groq.")
        return True
    elif "exit" in msg or "quit" in msg:
        speak("Goodbye, Sasi!")
        exit()
    return False

# Math handler
def handle_math(user_input):
    pattern = r'(\d+\.?\d*\s*[\+\-\*/]\s*\d+\.?\d*)'
    match = re.search(pattern, user_input)
    if match:
        try:
            result = eval(match.group())
            speak(f"The answer is {result}")
            return True
        except:
            speak("I couldn't calculate that.")
            return True
    return False

# Send to Groq API
def get_command_from_groq(user_input):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
    You are a smart Windows voice assistant that converts natural language into valid and safe CMD commands.

    🔒 Rules:
    - Only generate safe, non-destructive CMD commands.
    - Never include harmful commands (e.g., del, rm, format, regedit, shutdown).
    - Do not explain. Return CMD commands only.

    🧠 Supported Actions:
    1. **Open apps** (e.g., Notepad, Calculator, Chrome):
    - Examples: `start notepad`, `start calc`, `start chrome`

    2. **Type in Notepad** after opening:
    - Format:
        start notepad && powershell -command "Start-Sleep -s 2; Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('your text')"

    3. **Search in Chrome**:
    - Format:
        start chrome "https://www.google.com/search?q=your+search+query"

    4. **Open a website**:
    - Format:
        start chrome "https://example.com"

    User said: "{user_input}"

    Respond with the correct CMD command(s) only. No explanation or extra text.
    """

    data = {
        "messages": [{"role": "user", "content": prompt}],
        "model": GROQ_MODEL,
    }

    try:
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        result = response.json()

        if "choices" in result:
            groq_cmd = result["choices"][0]["message"]["content"].strip()

            if 'windows.explore' in groq_cmd.lower():
                groq_cmd = groq_cmd.replace('windows.explore', 'explorer')

            if re.match(r'http[s]?://', groq_cmd):
                groq_cmd = f'explorer {groq_cmd}'

            return groq_cmd
        else:
            raise ValueError("API response does not contain expected choices.")
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
        speak("Error communicating with the command service.")
        return "echo API Request Error"
    except ValueError as e:
        print(f"Value Error: {e}")
        speak("There was an error processing the command.")
        return "echo Command processing error"
    except Exception as e:
        print(f"Unknown Error: {e}")
        speak("Something went wrong while generating the command.")
        return "echo Unknown Error"

# Run command
def run_command(cmd):
    if is_restricted(cmd):
        speak("❌ Restricted command blocked for your safety.")
        log_command("Blocked", cmd)
    else:
        try:
            subprocess.run(cmd, shell=True)
            speak("✅ Done.")
            log_command("Executed", cmd)
        except Exception as e:
            print("Run Error:", e)
            speak("⚠️ Could not run the command.")
            log_command("Error", cmd)

# Main loop
def main():
    speak("Hello Sasi, your assistant is ready!")
    while True:
        user_input = listen()
        if not user_input:
            speak("Please say that again.")
            continue

        log_user_input(user_input)
        print("You said:", user_input)

        if handle_basic(user_input):
            continue

        if handle_math(user_input):
            continue

        groq_cmd = get_command_from_groq(user_input)
        print("Groq says:", groq_cmd)
        run_command(groq_cmd)

if __name__ == "__main__":
    main()
