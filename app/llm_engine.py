import os
from llama_cpp import Llama
from llama_cpp.llama_chat_format import Llava15ChatHandler

class LLMEngine:
    def __init__(self, model_path, context_size=2048):
        """
        Initializes the LLM Engine with a GGUF model.

        Args:
            model_path (str): Path to the .gguf file.
            context_size (int): Context window size.
        """
        self.model_path = model_path
        self.context_size = context_size
        self.llm = None

        # Check if model exists
        if not os.path.exists(model_path):
            print(f"Warning: Model not found at {model_path}. Please download it first.")
        else:
            self.load_model()

    def load_model(self):
        try:
            chat_handler = None

            # Simple heuristic for Vision support
            # Ideally, we should check model architecture from metadata, but filename is a good proxy for now.
            model_name_lower = self.model_path.lower()

            # If it's a known vision architecture that needs a handler (like LLaVA)
            # Qwen2-VL support in llama-cpp-python is improving but might still be experimental.
            # We will attempt to use Llava15ChatHandler for models labeled 'llava' or 'mmproj'.
            # For Qwen2-VL, current llama-cpp-python (0.3.x) often requires specifically setting up the clip model
            # or it might work if the GGUF bundles everything.
            # To avoid breaking the app, we will try to load it standard first, unless we are sure.

            # NOTE: For Qwen2-VL to work with image inputs in llama-cpp-python,
            # we usually need to rely on the 'chat_handler'.
            # However, initializing Llava15ChatHandler requires a 'clip_model_path'.
            # Since we are not downloading a separate mmproj file in the setup script (we download a single GGUF),
            # we assume the GGUF is "text-only" OR "integrated".
            # If it is integrated, we don't need a separate clip path for the handler,
            # BUT Llava15ChatHandler constructor mandates it.

            # DECISION: To ensure stability on an i3 laptop, we prioritize the Text capability.
            # If the user loads a Vision model without a separate projector, it acts as a text model.
            # We will NOT attach a broken chat_handler.
            # Instead, we will configure the Llama instance to be as permissive as possible.

            self.llm = Llama(
                model_path=self.model_path,
                n_ctx=self.context_size,
                n_gpu_layers=0, # CPU only
                verbose=False,
                logits_all=True
            )
            print(f"Model loaded successfully: {self.model_path}")
        except Exception as e:
            print(f"Error loading model: {e}")
            self.llm = None

    def create_chat_completion(self, messages, max_tokens=512, temperature=0.7, stream=True):
        """
        Uses the high-level chat_completion API.
        """
        if not self.llm:
             if stream:
                 yield {"choices": [{"delta": {"content": "Model not loaded."}}]}
             else:
                 return {"choices": [{"message": {"content": "Model not loaded."}}]}
             return

        # Sanitize messages for models that might crash with images
        # We try to pass it through first.
        try:
            return self.llm.create_chat_completion(
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=stream
            )
        except Exception as e:
            # Fallback: If it failed likely due to image_url not being supported by the model/handler
            # We remove image_urls and try again with just text.
            print(f"Generation failed (possibly vision issue), retrying with text only: {e}")

            sanitized_messages = []
            for msg in messages:
                new_content = ""
                if isinstance(msg["content"], list):
                    for part in msg["content"]:
                        if part["type"] == "text":
                            new_content += part["text"] + " "
                else:
                    new_content = msg["content"]

                sanitized_messages.append({"role": msg["role"], "content": new_content.strip()})

            if stream:
                 yield {"choices": [{"delta": {"content": "[Note: Image ignored because model/setup doesn't support it]\n\n"}}]}

            try:
                # Reuse the generator from the text-only call
                for chunk in self.llm.create_chat_completion(
                    messages=sanitized_messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    stream=stream
                ):
                    yield chunk
            except Exception as e2:
                 err_msg = f"Error during generation: {e2}"
                 if stream:
                     yield {"choices": [{"delta": {"content": err_msg}}]}
                 else:
                     return {"choices": [{"message": {"content": err_msg}}]}
