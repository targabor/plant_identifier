import streamlit as st
import requests
import json

def upload_image():
    st.header("Upload an Image")
    uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "jpeg", "png"])
    return uploaded_file

def capture_image():
    st.header("Capture an Image Using Camera")
    picture = st.camera_input('Plant input')
    return picture

def get_plant_name(input_picture):
    API_KEY = st.secrets["api"]["api_key"]  # Set you API_KEY here
    PROJECT = "all"  # try "weurope" or "canada"
    api_endpoint = f"https://my-api.plantnet.org/v2/identify/{PROJECT}?api-key={API_KEY}"

    image_bytes = input_picture.read()

    data = {
        'organs': ['auto']
    }

    files = [
        ('images', ("image.jpg", image_bytes))
    ]

    req = requests.Request('POST', url=api_endpoint, files=files, data=data)
    prepared = req.prepare()

    s = requests.Session()
    response = s.send(prepared)
    json_result = json.loads(response.text)

    st.write(json_result['results'][0])


if __name__ == "__main__":

    # Title of the app
    st.title("Plant Identifier")

    st.header("""Welcome to Plant Identifier!
    Easily identify and care for your plants with just a snap! :camera_with_flash::herb:
    Upload or take a picture of your plant, and our advanced model will recognize it and provide you with tailored care suggestions. Whether you're a seasoned gardener or a plant enthusiast, we've got the tools to help your greenery thrive.
    Start exploring your plants today!""")


    input_options = ["Upload file", "Capture an Image using Camera"]

    selection = st.radio("Choose a content:", input_options)

    if selection == "Upload file":
        picture = upload_image()
    elif selection == "Capture an Image using Camera":
        picture = capture_image()

    if picture is not None:
        st.image(picture, caption='Plant to be searched for', use_column_width=True)

    if st.button("Identify"):
        plant_name = get_plant_name(picture)
        st.header(plant_name)