"""Image preprocessing utilities for OCR enhancement."""

import io
from typing import Tuple
from PIL import Image, ImageEnhance, ImageOps

# Prevent decompression bomb DOS attacks
Image.MAX_IMAGE_PIXELS = 50_000_000


def preprocess_image_for_ocr(
    image_input: Image.Image | bytes,
    enhance_contrast: bool = True,
    target_dpi_width: int = 1600,
) -> Image.Image:
    """Preprocess an image to maximize Tesseract OCR character recognition accuracy.

    Steps applied:
    1. Safe loading and EXIF auto-orientation.
    2. Conversion to grayscale (L mode).
    3. DPI/dimension normalization (upscales small/low-res scans).
    4. Contrast enhancement to separate ink from background noise.

    Args:
        image_input: PIL Image or raw bytes.
        enhance_contrast: Whether to boost contrast for faint text.
        target_dpi_width: Ideal target pixel width for standard A4/US-Letter documents.

    Returns:
        Enhanced PIL Image in 'L' (grayscale) mode ready for OCR.
    """
    if isinstance(image_input, bytes):
        image = Image.open(io.BytesIO(image_input))
    else:
        image = image_input.copy()

    # Apply EXIF orientation if available (e.g. smartphone camera photo of report)
    try:
        image = ImageOps.exif_transpose(image)
    except Exception:
        pass

    # Convert to RGB first if CMYK or RGBA to avoid PIL conversion artifacts
    if image.mode in ("RGBA", "LA", "P"):
        background = Image.new("RGB", image.size, (255, 255, 255))
        if image.mode == "P":
            image = image.convert("RGBA")
        background.paste(image, mask=image.split()[-1])  # paste using alpha channel
        image = background
    elif image.mode != "RGB":
        image = image.convert("RGB")

    # Resize if image resolution is too low for OCR (standard text needs ~300 DPI)
    width, height = image.size
    if width < target_dpi_width:
        scale_factor = target_dpi_width / float(width)
        # Cap scaling factor to 3.0 to prevent excessive memory usage
        scale_factor = min(scale_factor, 3.0)
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        image = image.resize((new_width, new_height), resample=Image.Resampling.LANCZOS)

    # Convert to Grayscale
    grayscale = image.convert("L")

    # Enhance contrast
    if enhance_contrast:
        enhancer = ImageEnhance.Contrast(grayscale)
        grayscale = enhancer.enhance(1.8)

    return grayscale
