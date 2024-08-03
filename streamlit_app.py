import streamlit as st
import requests
import json
import os
from openai import AzureOpenAI

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

    try:
        specie = json_result['results'][0]['species']['commonNames'][0]
    except Exception as e:
        specie = None
    
    return specie

def openai_query(plant_name: str) -> str:
        # Set up OpenAI Client
        openai_api_key = st.secrets["azure"]["AZURE_OPENAI_API_KEY"]
        openai_endpoint = st.secrets["azure"]["AZURE_OPENAI_ENDPOINT"]
        openai_api_version = st.secrets["azure"]["API_VERSION"]
        client = AzureOpenAI(
            azure_endpoint=openai_endpoint,
            api_version=openai_api_version,
            api_key=openai_api_key
            )

        deployment_name=st.secrets["azure"]["AZURE_DEPLOYMENT"]

        print('Sending a test completion job')
        prompt = f"""
        I have a plant of species {plant_name}. Can you provide me with detailed care instructions for this plant? I'm interested in information on:
        1. **Light Requirements:** How much sunlight does it need?
        2. **Watering Needs:** How often should I water it, and are there any signs of overwatering or underwatering to look out for?
        3. **Soil and Fertilizer:** What type of soil is best, and how often should I fertilize it?
        4. **Temperature and Humidity:** What are the ideal temperature and humidity conditions for this plant?
        5. **Pest and Disease Control:** Are there common pests or diseases that affect this plant, and how can I manage them?
        Answer in bulletpoints, 2 sentence per bulletpoints, bulletpoints only, add one emoji for each bulletpoint.
        Use indicative mode. Don't include code or dialogs.
        """
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            )
        # print(prompt)
        # print("------RESPONSE-------")
        # print(response.to_dict()["choices"][0]["message"]["content"])
        return response.to_dict()["choices"][0]["message"]["content"]


    

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
        if plant_name: 
            st.header(plant_name)
            description = openai_query(plant_name)
            st.write(description)
        else:
            st.write("no luck this time🤔")