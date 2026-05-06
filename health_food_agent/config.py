from google.adk import Agent
 
DEFAULT_MODEL = "gemini-2.5-flash"
 
 
def create_agent(**kwargs) -> Agent:
    """Factory that injects default model if not specified."""
    kwargs.setdefault("model", DEFAULT_MODEL)
    return Agent(**kwargs)