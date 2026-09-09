from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import os


def generate_birthday_card(employee_name: str):

    image = Image.open(
        "assets/birthday_card_model.png"
    ).convert("RGBA")

    draw = ImageDraw.Draw(image)

    font = ImageFont.truetype(
        "assets/fonts/Poppins-Bold.ttf",
        36
    )
    
    x_position = 120
    y_position = 755

    draw.text(
        (x_position, y_position),
        employee_name,
        font=font,
        fill="#2A5CAA"
    )
    
    os.makedirs(
        "generated/cards",
        exist_ok=True
    )

    safe_name = employee_name.replace("/", "_")

    output_path = (
        f"generated/cards/{safe_name}.png"
    )

    image.save(output_path)

    return output_path
