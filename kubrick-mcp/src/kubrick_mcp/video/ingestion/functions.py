import pixeltable as pxt
from PIL import Image

@pxt.udf
def extract_text_from_chunk(transcript: pxt.type_system.Json) -> str:
    """
    Extract text from a transcript JSON object
    """
    return f"{transcript['text']}"


@pxt.udf
def resize_image(image: pxt.type_system.Image, width: int, height: int) -> pxt.type_system.Image:
    """
    Resize an image to fit within the specified width and height while maintaining aspect ratio.
    Note: The PIL.Image.thumbnail() method modifies the image in place
    """
    if not isinstance(image, Image.Image):
        raise TypeError("Input must be a PIL image")
    
    image.thumbnail((width, height))
    return image