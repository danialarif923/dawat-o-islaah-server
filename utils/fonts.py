from quran.models import CustomFont


def generate_fonts_css():

    css = ""

    for font in CustomFont.objects.all():

        css += f"""
@font-face {{
    font-family: "{font.name}";
    src: url("{font.file.url}") format("truetype");
    font-weight: normal;
    font-style: normal;
}}
"""
    return css
