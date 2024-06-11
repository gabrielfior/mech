from typing import Any, Dict, Optional, Tuple
from openai import OpenAI
from tiktoken import encoding_for_model

client: Optional[OpenAI] = None

class OpenAIClientManager:
    """Client context manager for OpenAI."""

    def __init__(self, api_key: str):
        self.api_key = api_key

    def __enter__(self) -> OpenAI:
        global client
        if client is None:
            client = OpenAI(api_key=self.api_key)
        return client

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        global client
        if client is not None:
            client.close()
            client = None

def count_tokens(text: str, model: str) -> int:
    """Count the number of tokens in a text."""
    enc = encoding_for_model(model)
    return len(enc.encode(text))


DEFAULT_DALLE_SETTINGS = {
    "size": "1024x1024",
    "quality": "standard",
    "n": 1,
}
PREFIX = "dall-e"
ENGINES = {
    "text-to-image": ["-2", "-3"],
}
ALLOWED_TOOLS = [PREFIX + value for value in ENGINES["text-to-image"]]
ALLOWED_SIZE = ["1024x1024", "1024x1792", "1792x1024"]
ALLOWED_QUALITY = ["standard", "hd"]


# @with_key_rotation
def run(**kwargs) -> Tuple[Optional[str], Optional[Dict[str, Any]], Any, Any]:
    """Run the task"""
    with OpenAIClientManager(kwargs["api_keys"]["openai"]):
        tool = kwargs["tool"]
        prompt = kwargs["prompt"]
        size = kwargs.get("size", DEFAULT_DALLE_SETTINGS["size"])
        quality = kwargs.get("quality", DEFAULT_DALLE_SETTINGS["quality"])
        n = kwargs.get("n", DEFAULT_DALLE_SETTINGS["n"])
        counter_callback = kwargs.get("counter_callback", None)
        if tool not in ALLOWED_TOOLS:
            return (
                f"Tool {tool} is not in the list of supported tools.",
                None,
                None,
                None,
            )
        if size not in ALLOWED_SIZE:
            return (
                f"Size {size} is not in the list of supported sizes.",
                None,
                None,
                None,
            )
        if quality not in ALLOWED_QUALITY:
            return (
                f"Quality {quality} is not in the list of supported qualities.",
                None,
                None,
                None,
            )

        response = client.images.generate(
            model=tool,
            prompt=prompt,
            size=size,
            quality=quality,
            n=n,
        )
        return response.data[0].url, prompt, None, counter_callback