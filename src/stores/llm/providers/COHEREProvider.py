from ..LLMInterface import LLMInterface
from ..LLMEnums import COHEREEnums, DocumentTypeEnums
import cohere
import logging

class COHEREProvider(LLMInterface):
        
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

                self.enums = COHEREEnums
                self.client = cohere.ClientV2(
                        api_key = self.api_key
                )

                self.logger = logging.getLogger(__name__)


        def set_generation_model(self, model_id: str):
            self.generation_model_id = model_id

        def set_embedding_model(self, model_id: str, embedding_size: int):
            self.embedding_model_id = model_id
            self.embedding_size = embedding_size

        def process_text(self, input_text: str):
            return input_text[:self.default_input_max_characters].strip()

        def generate_text(self, user_prompt: str, system_prompt: str = None,
                        chat_history: list = None,
                        max_output_tokens: int = None,
                        temperature: float = None):

            if not self.client:
                self.logger.error("COHERE client is not initialized. Please check your API key and URL.")
                return None

            if not self.generation_model_id:
                self.logger.error("Generation model ID is not set. Please set it using set_generation_model().")
                return None
            
            max_output_tokens = max_output_tokens if max_output_tokens is not None else self.default_generation_max_output_tokens

            temperature = temperature if temperature is not None else self.default_generation_temperature

            messages = list(chat_history or [])

            if system_prompt:
                messages.insert(
                    0,
                    self.construct_prompt(
                        prompt=system_prompt,
                        role=COHEREEnums.SYSTEM.value
                    )
                )

            messages.append(
                self.construct_prompt(
                    prompt=user_prompt,
                    role=COHEREEnums.USER.value
                )
            )

            response = self.client.chat(
                    model=self.generation_model_id,
                    messages=messages,
                    max_tokens=max_output_tokens,
                    temperature=temperature
            )
            if not response or not response.message.content:
                self.logger.error("Error while generating text with COHERE")
                return None    
            
            for content_item in response.message.content:
                if content_item.type == "text":
                    return content_item.text

        def embed_text(self, text: str, document_type: str = None):

            if not self.client:
                self.logger.error("COHERE client is not initialized. Please check your API key and URL.")
                return None

            if not self.embedding_model_id:
                self.logger.error("embedding model ID is not set. Please set it using set_embedding_model().")
                return None

            if not text or not text.strip():
                self.logger.error("Text parameter cannot be empty.")
                return None

            input_type : str = None

            if document_type == DocumentTypeEnums.QUERY.value:
                input_type = COHEREEnums.QUERY.value
            elif document_type == DocumentTypeEnums.DOCUMENT.value:
                input_type = COHEREEnums.DOCUMENT.value
            else:
                self.logger.error(f"Invalid or unsupported document_type: {document_type}")
                return None

            response = self.client.embed(
                model=self.embedding_model_id,
                texts=[text],
                input_type=input_type,
                embedding_types=["float"],
            )

            if not response or not response.embeddings or not response.embeddings.float_:
                self.logger.error("Error while Embedding text with COHERE")
                return None

            return response.embeddings.float_[0]
        

        def construct_prompt(self, prompt: str, role: str):

            return {
            'role' : role,
            'content' : prompt.strip()
        }
