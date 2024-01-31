import random

from pydantic import BaseModel


class ImageParams(BaseModel):
    """
    Serve as `input` and `parameters` in the request body of the /ai/generate-image endpoint.

    Except for the provided fields, other arbitrary fields can also be added into parameters,
    which will be present in the metadata of the image, like qualityToggle or ucPreset.
    These fields are mainly for the website to remember some key information when importing the image.

    Parameters
    ----------
    | Prompt
    prompt: `str`
        Text prompt to generate image from. Serve as `input` in the request body.
        Refer to https://docs.novelai.net/image/tags.html, https://docs.novelai.net/image/strengthening-weakening.html
    negative_prompt: `str`, optional
        Refer to https://docs.novelai.net/image/undesiredcontent.html
    qualityToggle: `bool`, optional
        Whether to automatically append quality tags to the prompt. Refer to https://docs.novelai.net/image/qualitytags.html
    ucPreset: `int`, optional
        Preset value of undisired content. Refer to https://docs.novelai.net/image/undesiredcontent.html
        Range: 0-3, 0: Heavy, 1: Light, 2: Human Focus, 3: None

    | Image settings
    width: `int`, optional
        Width of the image to generate in pixels
    height: `int`, optional
        Height of the image to generate in pixels
    n_samples: `int`, optional
        Number of images to return. The maximum value is 8 up to 360,448 px, 6 up to 409,600 px,
        4 up to 1,310,720 px, 2 up to 1,572,864 px, and 1 up to the max size

    | AI settings
    steps: `int`, optional
        Refer to https://docs.novelai.net/image/stepsguidance.html
    scale: `float`, optional
        Value of prompt guidance. Refer to https://docs.novelai.net/image/stepsguidance.html
    dynamic_thresholding: `bool`, optional
        Whether to enable descrisper. Refer to https://docs.novelai.net/image/stepsguidance.html#decrisper
    seed: `int`, optional
        Random seed to use for the image (between 0 and 4294967295), defaults to 0
        Seed 0 means that a random seed will be chosen, but not set in the metadata (so giving a seed yourself is important)
        Note: When generating multiple images, each consecutive image adds 1 to the seed parameter.
        This means it can go beyond the limit of 4294967295, making it unreproducible with a single generation
    extra_noise_seed: `int`, optional
        Unknown, but seems to be fulfill the same role as seed
    sampler: `str`, optional
        Refer to https://docs.novelai.net/image/sampling.html.
        The full list of samplers is (some may not work due to being deprecated): "k_lms", "k_euler",
        "k_euler_ancestral", "k_heun", "plms", "ddim", "nai_smea", "nai_smea_dyn", "k_dpmpp_2m",
        "k_dpmpp_2s_ancestral", "k_dpmpp_sde", "k_dpm_2", "k_dpm_2_ancestral", "k_dpm_adaptive", "k_dpm_fast"
    sm: `bool`, optional
        Whether to enable SMEA. Refer to https://docs.novelai.net/image/sampling.html#special-samplers-smea--smea-dyn
    sm_dyn: `bool`, optional
        Whether to enable SMEA DYN (SMEA needs to be enabled for SMEA DYN)
        Refer to https://docs.novelai.net/image/sampling.html#special-samplers-smea--smea-dyn
    uncond_scale: `float`, optional
        Range: 0-1.5, Undesired content strength, refer to https://docs.novelai.net/image/undesiredcontent.html#undesired-content-strength
    cfg_rescale: `int`, optional
        Range: 0-2, Prompt guidance rescale, refer to https://docs.novelai.net/image/stepsguidance.html#prompt-guidance-rescale
    noise_schedule: `str`, optional
        Noise schedule, choose from "native", "karras", "exponential", and "polyexponential"

    | img2img
    image: `str`, optional
        Base64-encoded PNG image for Image to Image
    strength: `float`, optional
        Range: 0.01-0.99, Refer to https://docs.novelai.net/image/strengthnoise.html
    noise: `float`, optional
        Range: 0-0.99, Refer to https://docs.novelai.net/image/strengthnoise.html
    controlnet_strength: `float`, optional
        Controls how much influence the ControlNet has on the image. Defaults to 1
    controlnet_condition: `str`, optional
        Base64-encoded PNG ControlNet mask retrieved from the /ai/annotate-image endpoint
    controlnet_model: `str`, optional
        Model to use for the ControlNet. Palette Swap is "hed", Form Lock is "depth",
        Scribbler is "scribble", Building Control is "mlsd", is Landscaper is "seg"

    | Inpaint
    add_original_image: `bool`, optional
        Refer to https://docs.novelai.net/image/inpaint.html#overlay-original-image
    mask: `str`, optional
        Base64-encoded black and white PNG image to use as a mask for inpainting
        White is the area to inpaint and black is the rest

    | Misc
    params_version: `int`, optional
        Defaults to 1
    legacy: `bool`, optional
        Defaults to False
    legacy_v3_extend: `bool`, optional
        Defaults to False
    """

    # Prompt
    prompt: str
    negative_prompt: str = ""
    qualityToggle: bool = True
    ucPreset: int = 2

    # Image settings
    width: int = 1024
    height: int = 1024
    n_samples: int = 1

    # AI settings
    steps: int = 28
    scale: float = 6
    dynamic_thresholding: bool = False
    seed: int = random.randint(0, 4294967295 - n_samples + 1)
    extra_noise_seed: int = random.randint(0, 4294967295 - n_samples + 1)
    sampler: str = "k_euler"
    sm: bool = True
    sm_dyn: bool = False
    uncond_scale: float = 1
    cfg_rescale: int = 0
    noise_schedule: str = "native"

    # img2img
    image: str | None = None
    strength: float | None = 0.3
    noise: float | None = 0
    controlnet_strength: float = 1
    controlnet_condition: str | None = None
    controlnet_model: str | None = None

    # Inpaint
    add_original_image: bool = True
    mask: str | None = None

    # Misc
    params_version: int = 1
    legacy: bool = False
    legacy_v3_extend: bool = False

    def model_post_init(self, *args) -> None:
        """
        Post-initialization hook. Inherit from `pydantic.BaseModel`.
        Implement this method to add custom initialization logic.
        """
        match self.ucPreset:
            case 0:  # Heavy
                self.negative_prompt += ", lowres, {bad}, text, error, missing, extra, fewer, cropped, jpeg artifacts, worst quality, bad quality, watermark, displeasing, unfinished, chromatic aberration, scan, scan artifacts, [abstract]"
            case 1:  # Light
                self.negative_prompt += ", lowres, jpeg artifacts, worst quality, watermark, blurry, very displeasing"
            case 2:  # Human Focus
                self.negative_prompt += ", lowres, {bad}, error, fewer, extra, missing, worst quality, jpeg artifacts, bad quality, watermark, unfinished, displeasing, chromatic aberration, signature, extra digits, artistic error, username, scan, [abstract], bad anatomy, bad hands, @_@, mismatched pupils, heart-shaped pupils, glowing eyes"

        if self.qualityToggle:
            self.prompt += ", best quality, amazing quality, very aesthetic, absurdres"

    def serialize(self) -> dict:
        """
        Convert the ImageParams object to a dictionary.

        Returns
        -------
        `dict`
            Dictionary containing the parameters
        """
        return self.model_dump(exclude=("prompt"), exclude_none=True)
