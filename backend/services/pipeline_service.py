import re
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

# In-memory storage for demo purposes
# In production, use Redis or a Database
_current_data = []

async def run_case_folding():
    global _current_data
    # Lowercase all text
    for item in _current_data:
        if 'text' in item:
            item['text'] = item['text'].lower()
    return {"status": "done", "step": "case_folding"}

async def run_url_removal():
    global _current_data
    # Remove URLs from text
    url_pattern = re.compile(r'https?://\S+|www\.\S+')
    for item in _current_data:
        if 'text' in item:
            item['text'] = url_pattern.sub('', item['text'])
    return {"status": "done", "step": "url_removal"}

async def run_stopwords():
    global _current_data
    # Use Sastrawi for Indonesian stopwords
    factory = StopWordRemoverFactory()
    stopword_remover = factory.create_stop_word_remover()

    for item in _current_data:
        if 'text' in item:
            item['text'] = stopword_remover.remove(item['text'])

    return {"status": "done", "step": "stopwords"}

async def run_emotion_detection():
    # Placeholder for Emotion Detection
    # Logic can be integrated with HuggingFace or similar models
    return {"status": "done", "step": "emotion"}

def set_current_data(data):
    global _current_data
    _current_data = data
