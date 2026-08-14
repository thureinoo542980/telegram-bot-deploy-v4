import os
import threading
import gradio as gr
from main import main as run_bot

def start_bot():
    """Starts the Telegram bot in a separate thread."""
    print("Starting Telegram Bot...")
    try:
        run_bot()
    except Exception as e:
        print(f"Bot error: {e}")

# Start the bot thread
bot_thread = threading.Thread(target=start_bot, daemon=True)
bot_thread.start()

# Define a simple Gradio interface to keep the Space alive and provide a health check
def greet(name="User"):
    return f"Drake Bot is running! Hello {name}."

iface = gr.Interface(
    fn=greet, 
    inputs="text", 
    outputs="text",
    title="Drake Telegram Bot",
    description="This service hosts the Drake Telegram Bot. The bot runs in the background."
)

if __name__ == "__main__":
    # Koyeb and other platforms use the PORT environment variable
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting Gradio server on port {port}")
    iface.launch(server_name="0.0.0.0", server_port=port)
