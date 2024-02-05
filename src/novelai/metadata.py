import math
import random
from typing import Literal, Annotated, override

from pydantic import BaseModel, Field, field_validator, model_validator

from .consts import MODELS, ACTIONS, SAMPLERS, NOISES, RESOLUTIONS


class Metadata(BaseModel):
    """
    Serve as `input` and `parameters` in the request body of the /ai/generate-image endpoint.

    Except for the provided fields, other arbitrary fields can also be added into parameters,
    which will be present in the metadata of the image, like qualityToggle or ucPreset.
    These fields are mainly for the website to remember some key information when importing the image.

    Parameters
    ----------
    | General
    prompt: `str`
        Text prompt to generate image from. Serve as `input` in the request body.
        Refer to https://docs.novelai.net/image/tags.html, https://docs.novelai.net/image/strengthening-weakening.html
    model: `str`, optional
        Model to use for the generation. Serve as `model` in the request body. Refer to `novelai.consts.MODELS`
    action: `str`, optional
        Action to perform. Serve as `action` in the request body. Refer to `novelai.consts.ACTIONS`

    | Note: all fields below that are not in "General" section will together serve as `parameters` in the request body

    | Prompt
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
    cfg_rescale: `float`, optional
        Range: 0-1, Prompt guidance rescale, refer to https://docs.novelai.net/image/stepsguidance.html#prompt-guidance-rescale
    noise_schedule: `str`, optional
        Noise schedule, choose from "native", "karras", "exponential", and "polyexponential"

    | img2img
    image: `str`, optional
        Base64-encoded PNG image for Image to Image
    strength: `float`, optional
        Range: 0.01-0.99, refer to https://docs.novelai.net/image/strengthnoise.html
    noise: `float`, optional
        Range: 0-0.99, refer to https://docs.novelai.net/image/strengthnoise.html
    controlnet_strength: `float`, optional
        Range: 0.1-2, controls how much influence the ControlNet has on the image
    controlnet_condition: `str`, optional
        Base64-encoded PNG ControlNet mask retrieved from the /ai/annotate-image endpoint
    controlnet_model: `str`, optional
        Control tool to use for the ControlNet. Note: V3 model does not support control tools
        Palette Swap is "hed", Form Lock is "depth", Scribbler is "scribble", Building Control is "mlsd", is Landscaper is "seg"

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

    # General
    # Fields in this section will be excluded from the output of model_dump during serialization
    prompt: str = Field(exclude=True)
    model: str = Field(default=MODELS.V3, exclude=True)
    action: str = Field(default=ACTIONS.GENERATE, exclude=True)

    # Prompt
    negative_prompt: str = ""
    qualityToggle: bool = True
    ucPreset: Literal[0, 1, 2, 3] = 2

    # Image settings
    width: Annotated[int, Field(ge=64, le=49152)] = 1024
    height: Annotated[int, Field(ge=64, le=49152)] = 1024
    n_samples: Annotated[int, Field(ge=1, le=8)] = 1

    # AI settings
    steps: int = Field(default=28, ge=1, le=50)
    scale: float = Field(default=6.0, ge=0, le=10, multiple_of=0.1)
    dynamic_thresholding: bool = False
    seed: int = Field(
        default_factory=lambda: random.randint(0, 4294967295 - 7),
        gt=0,
        le=4294967295 - 7,
    )
    extra_noise_seed: int = Field(
        default_factory=lambda: random.randint(0, 4294967295 - 7),
        gt=0,
        le=4294967295 - 7,
    )
    sampler: str = SAMPLERS.EULER
    sm: bool = True
    sm_dyn: bool = False
    uncond_scale: float = Field(default=1.0, ge=0, le=1.5, multiple_of=0.05)
    cfg_rescale: float = Field(default=0, ge=0, le=1, multiple_of=0.02)
    noise_schedule: str = NOISES.NATIVE

    # img2img
    image: str | None = None
    strength: float | None = Field(default=0.3, ge=0.01, le=0.99, multiple_of=0.01)
    noise: float | None = Field(default=0, ge=0, le=0.99, multiple_of=0.01)
    controlnet_strength: float = Field(default=1, ge=0.1, le=2, multiple_of=0.1)
    controlnet_condition: str | None = None
    controlnet_model: str | None = None

    # Inpaint
    add_original_image: bool = True
    mask: str | None = None

    # Misc
    params_version: Literal[1] = 1
    legacy: bool = False
    legacy_v3_extend: bool = False

    @field_validator("model")
    @classmethod
    def __model_validator(cls, v: str) -> str:
        if v not in MODELS.values():
            raise ValueError(f"Model should be in {list(MODELS.values())}")
        return v

    @field_validator("action")
    @classmethod
    def __action_validator(cls, v: str) -> str:
        if v not in ACTIONS.values():
            raise ValueError(f"Action should be in {list(ACTIONS.values())}")
        return v

    @field_validator("sampler")
    @classmethod
    def __sampler_validator(cls, v: str) -> str:
        if v not in SAMPLERS.values():
            raise ValueError(f"Sampler should be in {list(SAMPLERS.values())}")
        return v

    @field_validator("noise_schedule")
    @classmethod
    def __noise_schedule_validator(cls, v: str) -> str:
        if v not in NOISES.values():
            raise ValueError(f"Noise schedule should be in {list(NOISES.values())}")
        return v

    @model_validator(mode="after")
    def __n_samples_validator(self) -> "Metadata":
        max_n_samples = self.get_max_n_samples()
        if self.n_samples > max_n_samples:
            raise ValueError(
                f"Max value of n_samples is {max_n_samples} under current resolution ({self.width}x{self.height}). Got {self.n_samples}."
            )
        return self

    @override
    def model_post_init(self, *args) -> None:
        """
        Post-initialization hook. Inherit from `pydantic.BaseModel`.
        Implement this method to add custom initialization logic.
        """

        match self.ucPreset:
            case 0:  # Heavy
                self.negative_prompt += ", lowres, {bad}, error, fewer, extra, missing, worst quality, jpeg artifacts, bad quality, watermark, unfinished, displeasing, chromatic aberration, signature, extra digits, artistic error, username, scan, [abstract]"
            case 1:  # Light
                self.negative_prompt += ", lowres, jpeg artifacts, worst quality, watermark, blurry, very displeasing"
            case 2:  # Human Focus
                self.negative_prompt += ", lowres, {bad}, error, fewer, extra, missing, worst quality, jpeg artifacts, bad quality, watermark, unfinished, displeasing, chromatic aberration, signature, extra digits, artistic error, username, scan, [abstract], bad anatomy, bad hands, @_@, mismatched pupils, heart-shaped pupils, glowing eyes"

        if self.qualityToggle:
            self.prompt += ", best quality, amazing quality, very aesthetic, absurdres"

    def get_max_n_samples(self) -> int:
        """
        Get the max allowed number of images to generate in a single request by resolution.

        Returns
        -------
        `int`
            Maximum value of `ImageParams.n_samples`
        """

        w, h = self.width, self.height

        if w * h <= 512 * 704:
            return 8

        if w * h <= 640 * 640:
            return 6

        if w * h <= 1024 * 3072:
            return 4

        return 0

    def calculate_cost(self, is_opus: bool = False):
        """
        Calculate the Anlas cost of current parameters.

        Parameters
        ----------
        is_opus: `bool`, optional
            If the subscription tier is Opus. Opus accounts have access to free generations.
        """

        steps: int = self.steps
        n_samples: int = self.n_samples
        uncond_scale: float = self.uncond_scale
        strength: float = self.action == ACTIONS.IMG2IMG and self.strength or 1.0
        smea_factor = self.sm_dyn and 1.4 or self.sm and 1.2 or 1.0
        resolution = max(self.width * self.height, 65536)

        # For normal resolutions, squre is adjusted to the same price as portrait/landscape
        if resolution > math.prod(
            RESOLUTIONS.NORMAL_PORTRAIT
        ) and resolution <= math.prod(RESOLUTIONS.NORMAL_SQUARE):
            resolution = math.prod(RESOLUTIONS.NORMAL_PORTRAIT)

        per_sample = (
            math.ceil(
                2951823174884865e-21 * resolution
                + 5.753298233447344e-7 * resolution * steps
            )
            * smea_factor
        )
        per_sample = max(math.ceil(per_sample * strength), 2)

        if uncond_scale != 1.0:
            per_sample = math.ceil(per_sample * 1.3)

        opus_discount = (
            is_opus
            and steps <= 28
            and (resolution <= math.prod(RESOLUTIONS.NORMAL_SQUARE))
        )

        return per_sample * (n_samples - int(opus_discount))
