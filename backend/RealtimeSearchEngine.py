import requests
from bs4 import BeautifulSoup
import datetime
import os
from json import load, dump
from dotenv import dotenv_values
import cohere
from rich import print

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Assistant")
CohereAPIKey = env_vars.get("CohereAPIKey", "")

if not CohereAPIKey:
    raise ValueError("Cohere API key is missing in the .env file.")

# Initialize Cohere client
co = cohere.Client(api_key=CohereAPIKey)

def google_search(query):
    """
    Perform a Google search and return the top results as a summary.
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        }
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract search result snippets
        snippets = soup.select("div.BNeawe.vvjwJb.AP7Wnd")  # Extract result titles
        descriptions = soup.select("div.BNeawe.s3v9rd.AP7Wnd")  # Extract descriptions
        
        results = []
        for title, desc in zip(snippets, descriptions[:len(snippets)]):  # Combine title and description
            text = f"{title.get_text()}: {desc.get_text()}"
            if text and text not in results:
                results.append(text)
        
        if results:
            return "\n".join(results[:3])  # Return the top 3 results
        else:
            return f"Sorry, I couldn't find relevant information for '{query}'."
    except Exception as e:
        print(f"[red]Error during Google search:[/red] {e}")
        return "I'm sorry, an error occurred while fetching real-time information."

def RealtimeInformation(query=None):
    """
    Handles queries requiring real-time data by scraping Google or returning the current date/time.
    """
    now = datetime.datetime.now()
    if query:
        return google_search(query)
    return (
        f"Day: {now.strftime('%A')}\n"
        f"Date: {now.strftime('%d')}\n"
        f"Month: {now.strftime('%B')}\n"
        f"Year: {now.strftime('%Y')}\n"
        f"Time: {now.strftime('%H:%M:%S')}"
    )

# Example usage within the ChatBot function
def ChatBot(query):
    """
    Handles user queries, determining if they require real-time data or general responses.
    """
    try:
        chatlog_path = os.path.join("Data", "ChatLog.json")
        
        # Ensure chat log exists
        if not os.path.exists(chatlog_path):
            os.makedirs("Data", exist_ok=True)
            with open(chatlog_path, "w", encoding="utf-8") as f:
                dump([], f)

        # Load existing chat log
        with open(chatlog_path, "r", encoding="utf-8") as f:
            messages = load(f)

        messages.append({"role": "user", "content": query})

        # Determine query type
        query_type = "realtime" if "who" in query or "what" in query else "general"

        if "realtime" in query_type:
            response = RealtimeInformation(query)
        else:
            # Use Cohere API for general response
            completion = co.generate(
                model="command-xlarge-nightly",
                prompt=f"{Username}: {query}\n{Assistantname}:",
                max_tokens=100,
                temperature=0.7,
            )
            response = completion.generations[0].text.strip()

        # Save chat log
        messages.append({"role": "assistant", "content": response})
        with open(chatlog_path, "w", encoding="utf-8") as f:
            dump(messages, f, indent=4)

        return response

    except FileNotFoundError as e:
        print(f"[red]Chat log file not found:[/red] {e}")
        return "I'm sorry, an error occurred while accessing the chat log."
    except Exception as e:
        print(f"[red]Error in ChatBot:[/red] {e}")
        return "I'm sorry, an error occurred while processing your request."

# Entry point for standalone execution
if __name__ == "_main_":
    print(f"[green]{Assistantname} is ready! Type 'exit' or 'quit' to end the session.[/green]")
    while True:
        user_input = input(f"{Username}: ")
        if user_input.lower() in {"exit", "quit"}:
            print(f"[green]{Assistantname}: Goodbye![/green]")
            break
        print(f"[cyan]{Assistantname}:[/cyan] {ChatBot(user_input)}")