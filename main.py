import requests, os
from fastapi import FastAPI, HTTPException
from cerebras.cloud.sdk import Cerebras
from dataclasses import dataclass
from typing import TypeAlias, Literal

app = FastAPI()
client = Cerebras(api_key=os.environ.get("CEREBRAS_API_KEY"))
NINJA_KEY = os.environ.get("NINJAS_API_KEY")

Endpoints: TypeAlias = Literal["cerebras", "ninja"]
QuoteDict: TypeAlias = dict[str, bool | str]

@dataclass
class URLPaths:
    gen: str
    
    def get(self, endpoint: Endpoints) -> str:
        return f"{self.gen}/{endpoint}"

urls = URLPaths("/generate-quote")

@app.get(urls.get("cerebras"))
def get_cerebras_quote(vibe: str = "general love", language: str = "English") -> QuoteDict:
    """Generates a love quote with Cerebras."""
    
    system_prompt = f"""
    You are a modern world-class curator of romantic literature and a poetic translator.
    Your goal is to provide a beautiful, short love quote in {language}.
    The quotes should be short like a one-liner for maximum impact.
    An example of a quote you could make would be: "I want to be your favorite hello and your hardest goodbye."
    
    RULES:
    1. If a famous quote exists for the theme "{vibe}", provide it with the author's name.
    2. If no famous quote fits, generate an original, soul-stirring quote in the style of 19th-century or modern poets.
    3. The quote MUST be in {language}. If there are no quotes in {language}, then you can just translate it.
    4. FORMAT: "Quote text" \n— Author Name (or 'Unknown' if you wrote it).
    """
    
    user_prompt = f"Give me one heart-touching quote about {vibe}."
    
    try:
        response = client.chat.completions.create(
            model="llama3.1-8b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=1.0,
            top_p=0.9,
            max_tokens=600,
        )
        quote_text = response.choices[0].message.content
        return {"success": True, "text": quote_text}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get(urls.get("ninja"))
def get_ninja_quote() -> QuoteDict:
    """Fetches a pre-existing quote from API Ninjas."""
    try:
        api_url = "https://api.api-ninjas.com/v2/randomquotes?categories=love"
        response = requests.get(api_url, headers={"X-Api-Key": NINJA_KEY})
        
        if response.status_code == requests.codes.ok:
            data = response.json()[0] # API Ninjas returns a list
            return {
                "success": True, 
                "source": "api-ninjas", 
                "quote": data["quote"],
                "author": data["author"]
            }
        else:
            raise Exception(f"API Ninjas returned status {response.status_code}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
@app.head("/")
def health_check() -> dict[str, str]:
    """A simple ping endpoint to check if the server is awake."""
    return {
        "status": "Online",
        "message": "The Agapis Lapis Proxy is awake and ready!"
    }