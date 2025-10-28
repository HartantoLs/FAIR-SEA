# In: src/fairsea/__main__.py

from evaluationTest import analyze_sentiment

def main():
    """The main function that will be executed when the application runs."""
    
    print("=================================================")
    print("🚀 Welcome to the FAIR-SEA Toolkit! 🚀")
    print("=================================================")
    print("This is a standalone application built with PyInstaller.")
    
    
    # Example usage of a function from your toolkit
    text_to_analyze = "This is an excellent example of a successful project."
    sentiment = analyze_sentiment(text_to_analyze)
    
    print(f"\nSentiment analysis for text: '{text_to_analyze}'")
    print(f"Result: {sentiment}")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()