from ..LLMInterface import LLMInterface
from ..LLMEnums import GEMINIEnums
from google import genai
from google.genai import types

import logging


class GEMINIProvider(LLMInterface):
    
    def __init__(self, api_key: str,
                    default_input_max_characters: int=1000,
                    default_generation_max_output_tokens: int=1000,
                    default_generation_temperature: float=0.1):

                self.api_key=api_key

                self.default_input_max_characters=default_input_max_characters
                self.default_generation_max_output_tokens=default_generation_max_output_tokens
                self.default_generation_temperature=default_generation_temperature

                self.generation_model_id = None

                self.embedding_model_id = None
                self.embedding_size = None

                self.client = genai.Client(
                    api_key=self.api_key)

                self.logger = logging.getLogger(__name__)


    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id


    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    def process_text(self, input_text: str):
                return input_text[:self.default_input_max_characters].strip()


    def generate_text(self, prompt: str, chat_history: list = [] , 
                    max_output_tokens: int=None,
                    temperature: float=None):

            if not self.client:
                self.logger.error("GEMINI client is not initialized. Please check your API key.")
                return None

            if not self.generation_model_id:
                self.logger.error("Generation model ID is not set. Please set it using set_generation_model().")
                return None
            
            max_output_tokens = max_output_tokens if max_output_tokens is not None else self.default_generation_max_output_tokens

            temperature = temperature if temperature is not None else self.default_generation_temperature

            chat_history.append(
                self.construct_prompt(prompt=prompt, role=GEMINIEnums.USER.value)
            )

            response = self.client.models.generate_content(
                    model=self.generation_model_id,
                    contents=chat_history,
                    config=types.GenerateContentConfig(
                        max_output_tokens=max_output_tokens,
                        temperature=temperature
                    )
            )

            if not response or not response.text:
                self.logger.error("Error while generating text with GEMINI")
                return None    
            
            return response.text


    def embed_text(self, text: str, document_type: str = None):

        if not self.client:
            self.logger.error("GEMINI client is not initialized. Please check your API key.")
            return None

        if not self.embedding_model_id:
            self.logger.error("Embedding model ID is not set. Please set it using set_embedding_model().")
            return None

        if not text or not text.strip():
            self.logger.error("Text parameter cannot be empty.")
            return None

        response = self.client.models.embed_content(
            model=self.embedding_model_id,
            contents=[self.process_text(input_text=text)],
            config=types.EmbedContentConfig(
                output_dimensionality=self.embedding_size
            )
        )

        if not response or not response.embeddings or len(response.embeddings) == 0:
            self.logger.error("Error while Embedding text with GEMINI")
            return None

        return response.embeddings[0].values


    def construct_prompt(self, prompt: str, role: str) -> dict[str, str]:

        return {
            'role' : role,
            'parts' : [{'text': self.process_text(input_text=prompt)}]
        }