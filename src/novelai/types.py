import random

from pydantic import BaseModel


class User(BaseModel):
    username: str
    password: str

    def __str__(self):
        return f"User(username={self.username})"

    __repr__ = __str__


class ImageParams(BaseModel):
    """
    Serve as `parameters` in the request body of the /ai/generate-image endpoint.

    Except for the provided fields, other arbitrary fields can also be added into parameters,
    which will be present in the metadata of the image, like qualityToggle or ucPreset.
    These fields are mainly for the website to remember some key information when importing the image.

    Parameters
    ----------
    width: `int`
        Width of the image to generate in pixels
    height: `int`
        Height of the image to generate in pixels
    scale: `float`
        Value of prompt guidance. Refer to https://docs.novelai.net/image/stepsguidance.html
    sampler: `str`
        Refer to https://docs.novelai.net/image/sampling.html.
        The full list of samplers is (some may not work due to being deprecated): "k_lms", "k_euler",
        "k_euler_ancestral", "k_heun", "plms", "ddim", "nai_smea", "nai_smea_dyn", "k_dpmpp_2m",
        "k_dpmpp_2s_ancestral", "k_dpmpp_sde", "k_dpm_2", "k_dpm_2_ancestral", "k_dpm_adaptive", "k_dpm_fast"
    steps: `int`
        Refer to https://docs.novelai.net/image/stepsguidance.html
    n_samples: `int`
        Number of images to return. The maximum value is 8 up to 360,448 px, 6 up to 409,600 px,
        4 up to 1,310,720 px, 2 up to 1,572,864 px, and 1 up to the max size
    ucPreset: `int`
        Preset value of undisired content. Refer to https://docs.novelai.net/image/undesiredcontent.html
        Range: 0-3, 0: Heavy, 1: Light, 2: Human Focus, 3: None
    qualityToggle: `bool`
        Whether to automatically append quality tags to the prompt. Refer to https://docs.novelai.net/image/qualitytags.html
    sm: `bool`
        Whether to enable SMEA. Refer to https://docs.novelai.net/image/sampling.html#special-samplers-smea--smea-dyn
    sm_dyn: `bool`
        Whether to enable SMEA DYN (SMEA needs to be enabled for SMEA DYN)
        Refer to https://docs.novelai.net/image/sampling.html#special-samplers-smea--smea-dyn
    dynamic_thresholding: `bool`
        Whether to enable descrisper. Refer to https://docs.novelai.net/image/stepsguidance.html#decrisper
    seed: `int`
        Random seed to use for the image (between 0 and 4294967295), defaults to 0
        Seed 0 means that a random seed will be chosen, but not set in the metadata (so giving a seed yourself is important)
        Note: When generating multiple images, each consecutive image adds 1 to the seed parameter.
        This means it can go beyond the limit of 4294967295, making it unreproducible with a single generation
    extra_noise_seed: `int`
        Unknown, but seems to be fulfill the same role as Parameters.seed
    strength: `float`
        Range: 0.01-0.99, Refer to https://docs.novelai.net/image/strengthnoise.html
    noise: `float`
        Range: 0-0.99, Refer to https://docs.novelai.net/image/strengthnoise.html
    uncond_scale: `float`
        Range: 0-1.5, Undesired content strength, refer to https://docs.novelai.net/image/undesiredcontent.html#undesired-content-strength
    cfg_rescale: `int`
        Range: 0-2, Prompt guidance rescale, refer to https://docs.novelai.net/image/stepsguidance.html#prompt-guidance-rescale
    noise_schedule: `str`
        Noise schedule, choose from "native", "karras", "exponential", and "polyexponential"
    negative_prompt: `str`
        Refer to https://docs.novelai.net/image/undesiredcontent.html
    image: `str`
        Base64-encoded PNG image for Image to Image
    controlnet_condition: `str`
        Base64-encoded PNG ControlNet mask retrieved from the /ai/annotate-image endpoint
    controlnet_model: `str`
        Model to use for the ControlNet. Palette Swap is "hed", Form Lock is "depth",
        Scribbler is "scribble", Building Control is "mlsd", is Landscaper is "seg"
    controlnet_strength: `float`
        Controls how much influence the ControlNet has on the image
    add_original_image: `bool`
        Refer to https://docs.novelai.net/image/inpaint.html#overlay-original-image
    mask: `str`
        Base64-encoded black and white PNG image to use as a mask for inpainting
        White is the area to inpaint and black is the rest
    legacy: `bool`
        Defaults to False
    """

    width: int = 1024
    height: int = 1024
    scale: float = 5.5
    sampler: str = "k_euler"
    steps: int = 28
    n_samples: int = 1
    ucPreset: int = 0
    qualityToggle: bool = True
    sm: bool = True
    sm_dyn: bool = False
    dynamic_thresholding: bool = False
    seed: int = random.randint(0, 4294967295 - n_samples + 1)
    extra_noise_seed: int = random.randint(0, 4294967295 - n_samples + 1)
    strength: float = 0.3
    noise: float = 0
    uncond_scale: float = 1
    cfg_rescale: int = 0
    noise_schedule: str = "native"
    negative_prompt: str = "lowres, {bad}, text, error, missing, extra, fewer, cropped, jpeg artifacts, worst quality, bad quality, watermark, displeasing, unfinished, chromatic aberration, scan, scan artifacts, [abstract],"
    image: str = ""
    controlnet_condition: str = ""
    controlnet_model: str = ""
    controlnet_strength: float = 1
    add_original_image: bool = True
    mask: str = ""
    legacy: bool = False


class Image(BaseModel):
    """
    Image data.
    """

    data: bytes
    filename: str


class AuthError(Exception):
    """
    Exception for account authentication errors.
    """

    pass


class APIError(Exception):
    """
    Exception for package-level errors which need to be fixed in the future development (e.g. validation errors).
    """

    pass


class NovelAIError(Exception):
    """
    Exception for errors returned from NovelAI which are not handled by the package.
    """

    pass
