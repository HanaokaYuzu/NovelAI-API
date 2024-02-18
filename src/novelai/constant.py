from enum import Enum

from .types import HostInstance


HEADERS = {
    "Content-Type": "application/json",
    "Origin": "https://novelai.net",
    "Referer": "https://novelai.net",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}


class Host(Enum):
    API = HostInstance(
        url="https://api.novelai.net", accept="application/x-zip-compressed"
    )
    WEB = HostInstance(url="https://image.novelai.net", accept="binary/octet-stream")


class Endpoint(Enum):
    LOGIN = "/user/login"
    USERDATA = "/user/data"
    IMAGE = "/ai/generate-image"


class Model(Enum):
    # Anime V3
    V3 = "nai-diffusion-3"
    V3INP = "nai-diffusion-3-inpainting"

    # Furry model beta v1.3
    # Note that prompt preset in Metadata added by qualityToggle and ucPreset could be different,
    # but this module will not be specially adapted for it until a stable version is released.
    FURRY = "nai-diffusion-furry"
    FURRYINP = "furry-diffusion-inpainting"


class Controlnet(Enum):
    PALETTESWAP = "hed"
    FORMLOCK = "midas"
    SCRIBBLER = "fake_scribble"
    BUILDINGCONTROL = "mlsd"
    LANDSCAPER = "uniformer"


class Action(Enum):
    GENERATE = "generate"
    INPAINT = "infill"
    IMG2IMG = "img2img"


class Resolution(Enum):
    SMALL_PORTRAIT = (512, 768)
    SMALL_LANDSCAPE = (768, 512)
    SMALL_SQUARE = (640, 640)
    NORMAL_PORTRAIT = (832, 1216)
    NORMAL_LANDSCAPE = (1216, 832)
    NORMAL_SQUARE = (1024, 1024)
    LARGE_PORTRAIT = (1024, 1536)
    LARGE_LANDSCAPE = (1536, 1024)
    LARGE_SQUARE = (1472, 1472)
    WALLPAPER_PORTRAIT = (1088, 1920)
    WALLPAPER_LANDSCAPE = (1920, 1088)


class Sampler(Enum):
    EULER = "k_euler"
    EULER_ANC = "k_euler_ancestral"
    DPM = "k_dpmpp_2s_ancestral"


class Noise(Enum):
    NATIVE = "native"
    KARRAS = "karras"
    EXPONENTIAL = "exponential"
    POLYEXPONENTIAL = "polyexponential"
