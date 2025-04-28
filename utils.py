import base64

def image_to_base64(path):
    """Converte uma imagem em base64 para ser usada em HTML no Streamlit."""
    with open(path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()
    return encoded
