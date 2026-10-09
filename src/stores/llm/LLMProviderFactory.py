from .providers import OPENAIProvider, COHEREProvider, GEMINIProvider
from .LLMEnums import LLMEnums
from helpers.configurations import Settings


class LLMProviderFactory:
        
        """
            Factory class to create instances of LLM providers based on the provider name.
        """
        def __init__(self, configuration: Settings):
            """
            Initializes the LLMFactory with the given configuration.

            :param configuration: A Settings instance containing the configuration parameters for the providers.
            """
            self.configuration = configuration

        def get_llm_provider(self, provider_name: str):

            """
            Returns an instance of the specified LLM provider.

            :param provider_name: Name of the LLM provider (e.g., 'COHERE', 'OPENAI', 'GEMINI').
            :param configuration: A dictionary containing the configuration parameters for the provider.
            :return: An instance of the specified LLM provider.
            """ 
            if provider_name == LLMEnums.OPENAI.value:
                return OPENAIProvider(
                    api_key = self.configuration.OPENAI_API_KEY,
                    api_url = self.configuration.OPENAI_API_URL,
                    default_input_max_characters=self.configuration.INPUT_DAFAULT_MAX_CHARACTERS,
                    default_generation_max_output_tokens=self.configuration.GENERATION_DAFAULT_MAX_TOKENS,
                    default_generation_temperature=self.configuration.GENERATION_DAFAULT_TEMPERATURE
                )

            elif provider_name == LLMEnums.COHERE.value:
                return COHEREProvider(
                    api_key = self.configuration.COHERE_API_KEY,
                    default_input_max_characters=self.configuration.INPUT_DAFAULT_MAX_CHARACTERS,
                    default_generation_max_output_tokens=self.configuration.GENERATION_DAFAULT_MAX_TOKENS,
                    default_generation_temperature=self.configuration.GENERATION_DAFAULT_TEMPERATURE
                )

            elif provider_name == LLMEnums.GEMINI.value:
                return GEMINIProvider(
                    api_key = self.configuration.GEMINI_API_KEY,
                    default_input_max_characters=self.configuration.INPUT_DAFAULT_MAX_CHARACTERS,
                    default_generation_max_output_tokens=self.configuration.GENERATION_DAFAULT_MAX_TOKENS,
                    default_generation_temperature=self.configuration.GENERATION_DAFAULT_TEMPERATURE
                )
        
            else:
                raise ValueError(f"Unsupported LLM provider: {provider_name}")