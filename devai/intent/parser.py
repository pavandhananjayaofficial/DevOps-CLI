from devai.core.models import IntentCategory, ParsedIntent

class IntentParser:
    """
    Parses natural language into a structured intent.
    This could use a small local NLP model or basic heuristics/regex for simple commands.
    """
    
    def parse(self, text: str) -> ParsedIntent:
        text_lower = text.lower()
        category = IntentCategory.UNKNOWN
        
        if "deploy" in text_lower or "create" in text_lower or "build" in text_lower:
            category = IntentCategory.DEPLOY
        elif "destroy" in text_lower or "delete" in text_lower or "remove" in text_lower:
            category = IntentCategory.DESTROY
        elif "status" in text_lower or "show" in text_lower:
            category = IntentCategory.STATUS
            
        return ParsedIntent(
            original_text=text,
            category=category,
            confidence=0.8,
            extracted_entities={}
        )
