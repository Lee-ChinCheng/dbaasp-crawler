import requests
# conda activate base

# for our ghidorah server
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.1:8b"  


def call_ollama(prompt):
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload)

    if response.status_code == 200:
        return response.json().get("response").strip()
    else:
        return f"Error: {response.status_code}"


def is_biology_term(term):
    """
    a simple heuristic:
    - Many biological names follow binomial nomenclature (Genus species)
    - Capitalized first word + lowercase second word
    Then fallback to LLM if uncertain.
    """

    words = term.strip().split()

    # Heuristic check
    if len(words) == 2 and words[0][0].isupper() and words[1].islower():
        return True

    # Fallback to LLM classification
    prompt = f"""
    You are a classifier for a biology database chatbot.

    Task:
    Determine whether the user's message should be handled by a biology-domain chatbot.

    Important:
    - You are NOT a medical expert assistant here.
    - You do NOT answer questions.
    - You only classify scope.


    Determine if the following term is a biological term (e.g., organism, gene, protein, species, laboratory cell lines).
    Answer only "yes" or "no".

    Term: {term}
    """

    result = call_ollama(prompt).lower()

    return "yes" in result


def ask_ollama(term):
    """
    AI agent:
    - Check if input is biology term
    - If yes → return alias names as a list
    - If no → return message
    """

    if not is_biology_term(term):
        return "It's not a biology term."

    prompt = f"""
    You are a biology domain expert with strong knowledge of biological nomenclature and synonyms.

    Task:
    Provide common aliases, synonyms, or abbreviations for the biological term: "{term}".

    Requirements:
    - Return only a single line of output
    - Separate each alias with a comma
    - Each alias must be a concise string (no descriptions)
    - Do not repeat the original term unless it is commonly used in abbreviated form
    - Maximum of 6 aliases
    - No explanations, definitions, or extra text
    - If no widely recognized aliases exist, return: None

    Example:
    Input: Candida albicans
    Output: Candida albicans Berkhout, C. albicans, Monilia albicans
    """

    response = call_ollama(prompt)

    return response


if __name__ == '__main__':
    user_input = input("Enter a biology term: ")
    result = ask_ollama(user_input)
    print(result)
    





