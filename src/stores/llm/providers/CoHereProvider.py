from ..LLMInterface import LLMInterface
from ..LLMEnums import CoHereEnums, DocumentTypeEnum
import cohere
import logging
import json
class CoHereProvider(LLMInterface):

    def __init__(self, api_key: str,
                       default_input_max_characters: int=1000,
                       default_generation_max_output_tokens: int=1000,
                       default_generation_temperature: float=0.1):
        
        self.api_key = api_key

        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature

        self.generation_model_id = None

        self.embedding_model_id = None
        self.embedding_size = None
        self.enums = CoHereEnums
        self.client = cohere.ClientV2(api_key=self.api_key)

        self.logger = logging.getLogger(__name__)

    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    def process_text(self, text: str):
        return text[:self.default_input_max_characters].strip()

    def generate_text(self, prompt: str, chat_history: list=[], max_output_tokens: int=None,
                            temperature: float = None):

        if not self.client:
            self.logger.error("CoHere client was not set")
            return None

        if not self.generation_model_id:
            self.logger.error("Generation model for CoHere was not set")
            return None
        
        max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens
        temperature = temperature if temperature else self.default_generation_temperature

        messages=[
        {"role": chat_history[0]['role'], "content": chat_history[0]['text']} ,
        {
            "role": self.enums.USER.value,
            "content": self.process_text(prompt),
        },
        ]
        response = self.client.chat(
            model = self.generation_model_id,
            messages = messages,
            temperature = temperature,
            max_tokens = max_output_tokens
        )

        if not response or not response.message or not response.message.content[0] or not response.message.content[0]:
            self.logger.error("Error while generating text with CoHere")
            return None
        
        return json.dumps(response.message.content[0].dict(), ensure_ascii=False)
    
    def embed_text(self, text: str, document_type: str = None):
        if not self.client:
            self.logger.error("CoHere client was not set")
            return None

        if not self.embedding_model_id:
            self.logger.error("Embedding model for CoHere was not set")
            return None

        # Always use the .value for Enum members
        input_type = CoHereEnums.DOCUMENT.value
        if document_type == DocumentTypeEnum.QUERY.value:
            input_type = CoHereEnums.QUERY.value

        try:
            response = self.client.embed(
                model=self.embedding_model_id,
                texts=[self.process_text(text)],
                input_type=input_type,
                embedding_types=['float'],
            )
            # Use .get to avoid KeyError, ensure output is a list
            embeddings = getattr(response.embeddings, 'float', None)
            if not embeddings or not isinstance(embeddings, list):
                self.logger.error("Embeddings result is empty or invalid")
                return None
            return embeddings[0]
        except Exception as e:
            self.logger.error(f"Error embedding text with CoHere: {str(e)}")
            return None

    def construct_prompt(self, prompt: str, role: str):
        return {
            "role": role,
            "text": self.process_text(prompt)
        }
