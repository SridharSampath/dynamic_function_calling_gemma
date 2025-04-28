import json
from typing import Optional
from models import FunctionCall

def parse_function_call(response: str) -> Optional[FunctionCall]:
    """Parse the model's response to extract function calls"""
    try:
        response = response.strip()
        start_idx = response.find('{')
        end_idx = response.rfind('}') + 1
        
        if start_idx == -1 or end_idx == 0:
            return None
        
        json_str = response[start_idx:end_idx]
        data = json.loads(json_str)
        return FunctionCall(**data)
    except Exception as e:
        print(f"Error parsing function call: {str(e)}")
        return None