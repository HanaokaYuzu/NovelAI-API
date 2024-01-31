from .types import DotDict, Host

HOSTS = DotDict({
    "API": Host(url="https://api.novelai.net", accept="application/x-zip-compressed"),
    "WEB": Host(url="https://image.novelai.net", accept="binary/octet-stream"),
})

ENDPOINTS = DotDict({
    "LOGIN": "/user/login",
    "IMAGE": "/ai/generate-image",
})

MODELS = DotDict({
    "V3": "nai-diffusion-3",
    "V3INP": "nai-diffusion-3-inpainting",
})

HEADERS = {
    "Content-Type": "application/json",
    "Origin": "https://novelai.net",
    "Referer": "https://novelai.net",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}
