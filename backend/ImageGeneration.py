import os
import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import get_key
from time import sleep

# API details for the Hugging Face Stable Diffusion model
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {get_key('.env', 'HuggingFaceAPIKey')}"}

# Function to open and display images based on a given prompt
def open_images(prompt):
    folder_path = os.path.join(os.path.dirname(__file__), "Data")
    prompt = prompt.replace(" ", "_")
    files = [f"{prompt}_{i + 1}.jpg" for i in range(3)]

    for jpg_file in files:
        image_path = os.path.join(folder_path, jpg_file)
        if os.path.exists(image_path):
            try:
                img = Image.open(image_path)
                print(f"Opening image: {image_path}")
                img.show()
                sleep(1)
            except IOError:
                print(f"Unable to open {image_path}")
        else:
            print(f"File not found: {image_path}")

# Async function to send a query to the Hugging Face API
async def query(payload):
    for attempt in range(3):  # Retry logic
        try:
            response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
            print(f"API response status: {response.status_code}")
            if response.status_code == 200:
                print("API response content received successfully.")
                return response.content
            else:
                print(f"API Error (Attempt {attempt + 1}): {response.status_code}, {response.text}")
        except Exception as e:
            print(f"Error querying API (Attempt {attempt + 1}): {e}")
        sleep(2)  # Wait before retrying
    return None

# Wrapper function to generate and open images
async def generate_images(prompt: str):
    tasks = []
    for i in range(3):  # Restrict to 3 images
        payload = {
            "inputs": (
                f"{prompt}, detailed, photorealistic, cinematic lighting, "
                f"sharp focus, high resolution, seed={randint(0, 1000000)}"
            )
        }
        tasks.append(asyncio.create_task(query(payload)))

    image_bytes_list = await asyncio.gather(*tasks)

    folder_path = os.path.join(os.path.dirname(__file__), "Data")
    os.makedirs(folder_path, exist_ok=True)

    for i, image_bytes in enumerate(image_bytes_list):
        if image_bytes:
            file_path = os.path.join(folder_path, f"{prompt.replace(' ', '_')}_{i + 1}.jpg")
            try:
                with open(file_path, "wb") as f:
                    f.write(image_bytes)
                print(f"Image saved: {file_path}")
            except Exception as e:
                print(f"Failed to save image {i + 1}: {e}")
        else:
            print(f"Image generation failed for prompt: {prompt}, index: {i}")

    open_images(prompt)

# Main loop to monitor for image generation requests
def main():
    data_file_path = os.path.join(os.path.dirname(__file__), "../Frontend/Files/ImageGeneration.data")
    while True:
        try:
            if not os.path.exists(data_file_path):
                print("Data file not found. Retrying...")
                sleep(5)
                continue

            with open(data_file_path, "r") as f:
                data = f.read().strip()

            if not data:
                print("Data file is empty. Retrying...")
                sleep(5)
                continue

            try:
                prompt, status = data.split(",")
                status = status.strip().lower()
            except ValueError:
                print("Data file is malformed. Retrying...")
                sleep(5)
                continue

            if status == "true":
                print(f"Generating images for prompt: {prompt}")
                asyncio.run(generate_images(prompt))

                # Update the .data file to indicate completion
                with open(data_file_path, "w") as f:
                    f.write(f"{prompt},True")
            else:
                print("No new generation request. Retrying...")
                sleep(5)

        except Exception as e:
            print(f"An error occurred: {e}")
            sleep(5)

if __name__ == "__main__":
    main()
