import streamlit as st
import os
import requests
from bs4 import BeautifulSoup
from langchain_groq import ChatGroq
from langchain.schema import SystemMessage, HumanMessage
from sarvamai import SarvamAI

client = SarvamAI(
    api_subscription_key="sk_tw3vsy4n_LfieQoikM4paSA64meo8rc5x"
)

# Load Groq API key from environment variable
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
#if not GROQ_API_KEY:
#    st.error("Environment variable GROQ_API_KEY not set.")
#    st.stop()

# Sidebar input
st.sidebar.title("JD Translator")
url = st.sidebar.text_input("Enter Job Description URL:")
language = st.sidebar.selectbox("Translate to", ["Hindi", "Marathi", "Gujurati","Punjabi","Tamil", "Telugu"])

def translate_sarvam(text, target_lang):
    target = 'en-IN'
    
    if target_lang == 'Hindi':
        target = 'hi-IN'
    elif target_lang == 'Marathi':
        target = 'mr-IN'
    elif target_lang == 'Gujurati':
        target = 'gu-IN'
    elif target_lang == 'Punjabi':
        target = 'pa-IN'
    elif target_lang == 'Tamil':
        target = 'ta-IN'
    elif target_lang == 'Telugu':
        target = 'te-IN'

    response = client.text.translate(
    input=text,
    source_language_code="en-IN",
    target_language_code= target
    )
    print(response.translated_text)
    return response.translated_text

# Function to translate a given section using Groq
def translate_with_groq(text, target_lang):
    chat = ChatGroq(
        groq_api_key=GROQ_API_KEY,
        model_name= "llama-3.3-70b-versatile"#"gemma2-9b-it"
    )
    messages = [
        SystemMessage(
            content=(
                "You are a language translator. Translate the text clearly into the requested language. "
                "Do not translate organization names like 'Jio' or any acronyms or short forms (e.g., SIM, OTP, PAN, etc.). Only return the translated version. Do not explain anything."
            )
        ),
        HumanMessage(
            content=f"Translate to {target_lang}:\n{text}"
        )
    ]
    translated = chat.invoke(messages, temperature=0).content.strip()
    return translated

# Fetch, extract, translate, and update the HTML
def fetch_and_translate(url, target_lang):
    headers = {"User-Agent": "Mozilla/5.0"}
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")

    # IDs of the sections to be translated
    sections = [
        "MainContent_lblSummRole",     # Responsibilities
        "MainContent_lblSkill",        # Skills
        "MainContent_lblEduReq",       # Education
        "MainContent_lblExpReq"        # Experience
    ]

    for tag_id in sections:
        tag = soup.find("span", id=tag_id)
        if tag:
            original_text = tag.get_text(separator="\n", strip=True)
            translated = translate_sarvam(original_text, target_lang)
            translated = translated.replace("\n", "<br>")
            translated = BeautifulSoup(translated, "html.parser")
            tag.clear()
            tag.append(translated)
    return str(soup)

# Main app layout
if url and language:
    st.subheader("Translated Job Description")
    translated_html = fetch_and_translate(url, language)
    st.components.v1.html(translated_html, height=800, scrolling=True)