import os
from google import genai
from google.genai.types import GenerateContentConfig
from typing import List, Dict
import json

def ai_product_search(query: str, all_products: List[Dict]) -> List[int]:
    """
    Use Google Gemini AI to understand natural language search queries and return relevant product IDs
    
    Args:
        query: Natural language search query
        all_products: All available products
    
    Returns:
        List of product IDs ranked by relevance
    """
    
    if not query or len(all_products) == 0:
        return []
    
    # Prepare product catalog for AI
    product_descriptions = "\n".join([
        f"ID {p['id']}: {p['name']} - {p.get('description', '')} - Category: {p.get('category', {}).get('name', 'N/A') if p.get('category') else 'N/A'} - ${p['price']}"
        for p in all_products[:100]
    ])
    
    prompt = f"""You are a fashion search assistant for Z'ss, a luxury clothing brand.

User Query: "{query}"

Available Products:
{product_descriptions}

Based on the user's query, return the IDs of the most relevant products. Consider:
- Natural language understanding (e.g., "comfortable" → activewear, soft fabrics)
- Intent (e.g., "wedding" → formal attire)
- Price mentions (e.g., "under $50")
- Style keywords (e.g., "casual", "formal", "summer")
- Synonyms and related concepts

Return ONLY a JSON array of up to 20 product IDs, ordered by relevance.
Example: [5, 12, 3, 8, 15]

Do not include any explanation, just the JSON array.
"""
    
    try:
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt
        )
        
        result_text = response.text.strip()
        result_text = result_text.replace('```json', '').replace('```', '').strip()
        product_ids = json.loads(result_text)
        
        product_ids = [int(id) for id in product_ids if isinstance(id, (int, str)) and str(id).isdigit()]
        return product_ids[:20]
    
    except Exception as e:
        print(f"Gemini AI search error: {e}")
        return []