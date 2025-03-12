def RealtimeSearchEngine(prompt):
    try:
        print(f"Debug: Received Prompt: {prompt}")
        
        # Perform Google Search and capture results
        google_results = GoogleSearch(prompt)
        print(f"Debug: Google Search Results:\n{google_results}")
        
        # Fetch real-time information
        real_time_info = Information()
        print(f"Debug: Real-Time Information:\n{real_time_info}")
        
        # Mock response for chatbot
        Answer = f"Mock response for the query: {prompt}\n\n"
        Answer += f"Google Search Results:\n{google_results}\n\n"
        Answer += f"Real-Time Info:\n{real_time_info}"
        
        print(f"Debug: Final Answer:\n{Answer}")
        return Answer
    except Exception as e:
        print(f"Debug: Error Occurred: {str(e)}")
        return f"An error occurred: {str(e)}"

if __name__ == "__main__":
    while True:
        try:
            # Capture user input
            prompt = input("Enter your Query: ").strip()
            if not prompt:
                print("Debug: No query entered. Please try again.")
                continue
            
            # Process query using RealtimeSearchEngine
            response = RealtimeSearchEngine(prompt)
            
            # Output the response
            print(f"\nResponse:\n{response}")
        except KeyboardInterrupt:
            print("\nExiting program.")
            break
