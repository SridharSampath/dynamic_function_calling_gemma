import gradio as gr
import ollama
from config import MODEL_NAME
from models import SearchParameters, TranslateParameters, WeatherParameters
from functions.search import google_search
from functions.translate import translate_text
from functions.weather import get_weather
from utils.parse_function_call import parse_function_call

# System message for the model
SYSTEM_MESSAGE = """
You are an AI assistant with training data up to 2023. 
Answer questions directly when possible, and use function calling when necessary.

DECISION PROCESS:
1. For historical events (before 2023):
   → Answer directly from your training data.

2. For current events (after 2023):
   → ALWAYS use 'google_search'. Never guess.

3. For real-time data (e.g., sports winners, current CEO, stock prices, event schedules):
   → ALWAYS use 'google_search'.

4. For translation requests (e.g., "Translate 'Hello' to Spanish"):
   → Use 'translate_text' function.

5. For weather-related questions (e.g., "What's the weather in Chennai?"):
   → Use 'get_weather' function.

IMPORTANT RULES:
- When calling a function, respond ONLY with the JSON object, no additional text, no backticks.
- When answering directly from memory, respond ONLY in clean natural language text, NOT in JSON.

WHEN TO FETCH WEATHER (Mandatory):
- If the user asks about "weather", "temperature", "climate", "forecast", or "current weather" — ALWAYS call the 'get_weather' function.
- NEVER answer weather questions from memory, even if you answered a similar query before.
- Each weather query must always trigger a fresh 'get_weather' API call.

WHEN TO SEARCH (Mandatory):
- If the question mentions dates after 2023 (e.g., "AWS re:Invent 2025", "Olympics 2028")
- If the question contains words like "current", "latest", "now", "today", "recent", "new", "future".
- If the user asks about ongoing events, upcoming conferences, tournaments, elections, weather.
- If you are unsure about the information.
- DO NOT guess or invent dates or details.


FUNCTION CALL FORMAT (Strict):
Example for Search:
{
    "name": "google_search",
    "parameters": {
        "query": "your search query here"
    }
}

Example for Translation:
{
    "name": "translate_text",
    "parameters": {
        "text": "Text to translate",
        "target_language": "language code (e.g., fr, es, de)"
    }
}

Example for Weather:
{
    "name": "get_weather",
    "parameters": {
        "city": "City name (e.g., Chennai, Paris)"
    }
}

SEARCH FUNCTION:
{
    "name": "google_search",
    "description": "Search for real-time information like current events, latest news, updates, dates",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query"
            }
        },
        "required": ["query"]
    }
}

TRANSLATE FUNCTION:
{
    "name": "translate_text",
    "description": "Translate given text into the target language",
    "parameters": {
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "Text to translate"
            },
            "target_language": {
                "type": "string",
                "description": "Target language code (e.g., fr, es, de)"
            }
        },
        "required": ["text", "target_language"]
    }
}

WEATHER FUNCTION:
{
    "name": "get_weather",
    "description": "Fetch real-time weather information for a given city",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "City name"
            }
        },
        "required": ["city"]
    }
}

RESPONSE GUIDELINES:
- Only include facts directly from the search/translation/weather result.
- Never invent or assume information not provided.
- Quote dates, names, facts exactly as retrieved.
- Keep responses concise and factual.
- If using memory knowledge (pre-2023), respond naturally without any JSON.

VERY IMPORTANT:
- If you are answering from memory (no function call needed), respond ONLY in natural human-readable text, NOT JSON structure.
- Do NOT format memory answers as JSON.
- JSON format must be used only for function calls.

"""

# Define the process_message function
def process_message(user_input, chat_history):
    try:
        chat_history.append({"role": "user", "content": user_input})
        info = None

        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_MESSAGE},
                {"role": "user", "content": user_input}
            ]
        )

        model_response = response['message']['content']

        function_call = parse_function_call(model_response)

        if function_call:
            if function_call.name == "google_search":
                search_params = SearchParameters(**function_call.parameters)
                search_query = search_params.query

                # Step 1: Announce search happening
                info = f"🔍 Searching for: {search_query}"
                chat_history.append({"role": "assistant", "content": info})
                yield chat_history

                # Step 2: Actually perform the search
                search_result = google_search(search_query)

                # Step 3: Announce fetched result
                chat_history.append({"role": "assistant", "content": f"🔍 Google Search fetched using Serper API:\n\n{search_result.to_string()}"})
                yield chat_history

                assistant_response = f"🔍 Answered via Search:\n\n{search_result.to_string()}"

            elif function_call.name == "translate_text":
                translate_params = TranslateParameters(**function_call.parameters)
                input_text = translate_params.text
                target_lang = translate_params.target_language

                # Step 1: Announce translation happening
                info = f"🌐 Translating text to {target_lang}"
                chat_history.append({"role": "assistant", "content": info})
                yield chat_history

                # Step 2: Actually perform translation
                translated_result = translate_text(input_text, target_lang)

                # Step 3: Announce fetched result
                chat_history.append({"role": "assistant", "content": f"🌐 Translation fetched using MyMemory API:\n\n{translated_result}"})
                yield chat_history

                assistant_response = f"🌐 Answered via Translation:\n\n{translated_result}"

            elif function_call.name == "get_weather":
                weather_params = WeatherParameters(**function_call.parameters)
                city_name = weather_params.city

                # Step 1: Announce weather fetching
                info = f"⛅ Fetching weather for: {city_name}"
                chat_history.append({"role": "assistant", "content": info})
                yield chat_history

                # Step 2: Actually fetch weather
                weather_result = get_weather(city_name)

                # Step 3: Announce fetched result
                chat_history.append({"role": "assistant", "content": f"⛅ Weather fetched using OpenWeatherMap API:\n\n{weather_result}"})
                yield chat_history

                assistant_response = f"⛅ Answered via Weather:\n\n{weather_result}"

            else:
                assistant_response = model_response

        else:
            assistant_response = model_response

        chat_history.append({"role": "assistant", "content": f"✨ Response:\n{assistant_response}"})
        yield chat_history

    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        chat_history.append({"role": "assistant", "content": error_msg})
        yield chat_history

# Define Gradio Interface
with gr.Blocks(css="footer {visibility: hidden}") as demo:

    # Static header / app description
    gr.Markdown("""
    # 🤖 Dynamic Function Calling - Powered by Gemma 3 🔍 🌐 ⛅

    This chatbot intelligently uses:
    - 🔍 Real-time search (via Serper API)
    - 🌐 Language translation (via MyMemory API)
    - ⛅ Weather updates (via OpenWeatherMap)

    Powered locally using **Gemma 3 model with Ollama**.
    """)
    
    gr.Markdown("---")

    chatbot = gr.Chatbot(
        height=500,
        show_label=False,
        avatar_images=(None, "https://api.dicebear.com/7.x/bottts/svg?seed=gemma"),
        type="messages"
    )
    
    gr.Markdown("---")

    with gr.Row():
        msg = gr.Textbox(
            scale=5,
            show_label=False,
            placeholder="Ask me anything (search, translate, weather)...",
            container=False
        )
        submit_btn = gr.Button("Send", scale=1)

    with gr.Row():
        clear_btn = gr.Button("Clear Chat")

    msg.submit(process_message, [msg, chatbot], [chatbot])
    submit_btn.click(process_message, [msg, chatbot], [chatbot])
    clear_btn.click(lambda: [], None, chatbot, queue=False)

    msg.submit(lambda: "", None, msg)
    submit_btn.click(lambda: "", None, msg)

# Launch Gradio app
if __name__ == "__main__":
    demo.launch(inbrowser=True, share=True)
