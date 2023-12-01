import os
from typing import Iterator, List, Tuple

from text_generation import Client

model_id = "mistralai/Mistral-7B-Instruct-v0.1"

API_URL = "https://api-inference.huggingface.co/models/" + model_id
HF_TOKEN = os.environ.get("HF_READ_TOKEN", None)

client = Client(
    API_URL,
    headers={"Authorization": f"Bearer {HF_TOKEN}"},
)
EOS_STRING = "</s>"
EOT_STRING = "<EOT>"


def _get_prompt(
    message: str, chat_history: List[Tuple[str, str]], system_prompt: str
) -> str:
    """
    Get the prompt to send to the model.
    :param message: The message to send to the model.
    :param chat_history: The chat history.
    :param system_prompt: The system prompt.
    :return: The prompt to send to the model.
    """
    texts = [f"<s>[INST] <<SYS>>\n{system_prompt}\n<</SYS>>\n\n"]
    do_strip = False
    for user_input, response in chat_history:
        user_input = user_input.strip() if do_strip else user_input
        do_strip = True
        texts.append(f"{user_input} [/INST] {response.strip()} </s><s>[INST] ")
    message = message.strip() if do_strip else message
    texts.append(f"{message} [/INST]")
    return "".join(texts)


def run(
    message: str,
    chat_history: List[Tuple[str, str]],
    system_prompt: str,
    max_new_tokens: int = 2048,
    temperature: float = 0.1,
    top_p: float = 0.9,
    top_k: int = 50,
) -> Iterator[str]:
    """
    Run the model.
    :param message: The message to send to the model.
    :param chat_history: The chat history.
    :param system_prompt: The system prompt.
    :param max_new_tokens: The maximum number of tokens to generate.
    :param temperature: The temperature.
    :param top_p: The top p.
    :param top_k: The top k.
    :return: The generated text.
    """
    prompt = _get_prompt(message, chat_history, system_prompt)

    generate_kwargs = dict(
        max_new_tokens=max_new_tokens,
        do_sample=True,
        top_p=top_p,
        top_k=top_k,
        temperature=temperature,
    )
    stream = client.generate_stream(prompt, **generate_kwargs)
    output = ""
    for response in stream:
        if any(
            [end_token in response.token.text for end_token
             in [EOS_STRING, EOT_STRING]]
        ):
            return output
        else:
            output += response.token.text
        yield output
    return output
