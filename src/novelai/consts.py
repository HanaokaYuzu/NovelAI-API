from .types import DotDict, Host

HOSTS = DotDict(
    {
        "API": Host(
            url="https://api.novelai.net", accept="application/x-zip-compressed"
        ),
        "WEB": Host(url="https://image.novelai.net", accept="binary/octet-stream"),
    }
)

ENDPOINTS = DotDict(
    {
        "LOGIN": "/user/login",
        "USERDATA": "/user/data",
        "IMAGE": "/ai/generate-image",
    }
)

MODELS = DotDict(
    {
        "V3": "nai-diffusion-3",
        "V3INP": "nai-diffusion-3-inpainting",
    }
)

ACTIONS = DotDict(
    {
        "GENERATE": "generate",
        "INPAINT": "infill",
        "IMG2IMG": "img2img",
    }
)

RESOLUTIONS = DotDict(
    {
        "SMALL_PORTRAIT": (512, 768),
        "SMALL_LANDSCAPE": (768, 512),
        "SMALL_SQUARE": (640, 640),
        "NORMAL_PORTRAIT": (832, 1216),
        "NORMAL_LANDSCAPE": (1216, 832),
        "NORMAL_SQUARE": (1024, 1024),
        "LARGE_PORTRAIT": (1024, 1536),
        "LARGE_LANDSCAPE": (1536, 1024),
        "LARGE_SQUARE": (1472, 1472),
        "WALLPAPER_PORTRAIT": (1088, 1920),
        "WALLPAPER_LANDSCAPE": (1920, 1088),
    }
)

SAMPLERS = DotDict(
    {
        "EULER": "k_euler",
        "EULER_ANC": "k_euler_ancestral",
        "DPM": "k_dpmpp_2s_ancestral",
    }
)

NOISES = DotDict(
    {
        "NATIVE": "native",
        "KARRAS": "karras",
        "EXPONENTIAL": "exponential",
        "POLYEXPONENTIAL": "polyexponential",
    }
)

HEADERS = {
    "Content-Type": "application/json",
    "Origin": "https://novelai.net",
    "Referer": "https://novelai.net",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}
