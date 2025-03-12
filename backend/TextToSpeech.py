import pygame  # Import pygame library for handling audio playback
import random  # Import random for generating random choices
import asyncio  # Import asyncio for asynchronous operations
import edge_tts  # Import edge_tts for text-to-speech functionality
import os  # Import os for file path handling
from dotenv import dotenv_values  # Import dotenv for reading environment variables from a .env file

# Load environment variables from a .env file
env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistantVoice")  # Get the AssistantVoice from the environment variables

# Validate the voice before proceeding
valid_voices = [
    "en-US-GuyNeural", "en-US-JessaNeural", "en-GB-RyanNeural", "en-GB-SusanNeural",
    "enAU-SteveNeural", "enCA-LiamNeural", "enIN-AditiNeural", "enIN-RameshNeural"
]

if AssistantVoice not in valid_voices:
    print(f"Error: Invalid voice '{AssistantVoice}'. Using default voice 'en-US-GuyNeural'.")
    AssistantVoice = "en-US-GuyNeural"  # Fall back to a default valid voice

# Asynchronous function to convert text to an audio file
async def TextToAudioFile(text) -> None:
    directory = "Data"  # Directory where the speech file will be saved
    file_path = os.path.join(directory, "speech.mp3")  # Define the path for the MP3 file
    
    # Ensure the directory exists
    if not os.path.exists(directory):
        os.makedirs(directory)  # Create the directory if it doesn't exist
    
    try:
        # Create the communicate object to generate speech
        print(f"Generating speech for text: {text}")  # Log the text being converted to speech
        communicate = edge_tts.Communicate(text, AssistantVoice, pitch='+5Hz', rate='+13%')
        await communicate.save(file_path)  # Save the generated speech as an MP3 file
        print(f"Speech saved to: {file_path}")  # Log success
        
        # Check if the file was actually saved
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Failed to save the speech file: {file_path}")
        
    except Exception as e:
        print(f"Error while generating speech: {e}")

# Function to manage Text-to-Speech (TTS) functionality
def TTS(Text, func=lambda r=None: True):
    pygame.mixer.init()  # Initialize pygame mixer for audio playback (moved here for proper initialization)
    
    while True:
        try:
            # Convert text to an audio file asynchronously
            asyncio.run(TextToAudioFile(Text))
            
            # Check if the file exists before loading
            file_path = os.path.join("Data", "speech.mp3")
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"The file {file_path} was not found after speech generation.")
            
            # Load the generated speech file into pygame mixer
            print(f"Loading and playing the file: {file_path}")  # Log the file being loaded
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()  # Start playing the music
            
            # Wait until the audio has finished playing or an external function stops it
            while pygame.mixer.music.get_busy():
                if func() == False:  # Check if the external function returns False
                    break
                pygame.time.Clock().tick(10)  # Limit the loop to 10 ticks per second
            return True  # Return True if the audio played successfully
        
        except Exception as e:  # Handle any exceptions during the process
            print(f"Error in TTS: {e}")
        
        finally:
            try:
                # Call the provided function with False to signal the end of TTS
                func(False)
                pygame.mixer.music.stop()  # Stop the audio playback
                pygame.mixer.quit()  # Quit the pygame mixer
            except Exception as e:  # Handle any exceptions during cleanup
                print(f"Error in finally block: {e}")

# Function to manage Text-to-Speech with additional responses for long text
def TextToSpeech(Text, func=lambda r=None: True):
    Data = str(Text).split(".")  # Split the text by periods into a list of sentences
    
    # List of predefined responses for cases where the text is too long
    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out sir.",
        "The rest of the text is now on the chat screen, sir, please check it.",
        "You can see the rest of the text on the chat screen, sir.",
        "The remaining part of the text is now on the chat screen, sir.",
        "Sir, you'll find more text on the chat screen for you to see.",
        "The rest of the answer is now on the chat screen, sir.",
        "Sir, please look at the chat screen, the rest of the answer is there.",
        "You'll find the complete answer on the chat screen, sir.",
        "The next part of the text is on the chat screen, sir.",
        "Sir, please check the chat screen for more information.",
        "There's more text on the chat screen for you, sir.",
        "Sir, take a look at the chat screen for additional text.",
        "You'll find more to read on the chat screen, sir.",
        "Sir, check the chat screen for the rest of the text.",
        "The chat screen has the rest of the text, sir.",
        "There's more to see on the chat screen, sir, please look.",
        "Sir, the chat screen holds the continuation of the text.",
        "You'll find the complete answer on the chat screen, kindly check it out sir.",
        "Please review the chat screen for the rest of the text, sir.",
        "Sir, look at the chat screen for the complete answer."
    ]
    
    # If the text is very long (more than 4 sentences and 250 characters), add a response message
    if len(Data) > 4 and len(Text) > 250:
        TTS(" ".join(Text.split(".")[0:2]) + ". " + random.choice(responses), func)
    
    # Otherwise, just play the whole text
    else:
        TTS(Text, func)

# Main execution loop
if __name__ == "_main_":
    while True:
        # Prompt user for input and pass it to TextToSpeech function
        TextToSpeech(input("Enter the text: "))