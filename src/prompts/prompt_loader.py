import yaml
import json
from typing import Dict, Any
from pydantic import BaseModel

class PromptLoader:
    def __init__(self, prompt_file_path: str = 'prompts.yaml'):
        self.prompt_file_path = prompt_file_path
        self._prompts = self._load_prompts()

    def _load_prompts(self) -> Dict[str, Any]:
        with open(self.prompt_file_path, 'r') as file:
            _prompts = yaml.safe_load(file)
        return _prompts

    def get_prompt(self, prompt_key, sub_key=None, **kwargs) -> str:
        try:
            prompt = self._prompts[prompt_key]
            if sub_key is not None:
                prompt = prompt[sub_key]
            if "schema_class" in kwargs:
                schema_model = kwargs.pop("schema_class")
                if issubclass(schema_model, BaseModel):
                    kwargs ['json_schema'] = json.dumps(schema_model.model_json_schema(), indent=2)
        
            return prompt.format(**kwargs)
        except KeyError:
            raise KeyError(f"Prompt key '{prompt_key}.{sub_key}' not found in {self.prompt_file_path}")
        