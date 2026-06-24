from PIL import Image

def process_photo(photo_path: str, output_path: str):
    img = Image.open(photo_path)
    img = img.convert("RGB")
    img.thumbnail((300, 300))
    img.save(output_path)
    return output_path