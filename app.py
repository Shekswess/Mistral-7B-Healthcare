import os
from typing import Iterator

import gradio as gr

from src.model import run

HF_PUBLIC = os.environ.get("HF_PUBLIC", False)

DEFAULT_SYSTEM_PROMPT = "You are Mistral. You are AI-assistant, you are polite, give only truthful information and are based on the Mistral-7B model from Mistral AI. You can communicate in different languages equally well."
MAX_MAX_NEW_TOKENS = 4096
DEFAULT_MAX_NEW_TOKENS = 256
MAX_INPUT_TOKEN_LENGTH = 4000

DESCRIPTION = """
# [Mistral-7B](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.1)
"""


def clear_and_save_textbox(message: str) -> tuple[str, str]:
    """
    Clear the textbox and save the input to a state variable.
    :param message: The input message.
    :return: A tuple of the empty string and the input message.
    """
    return "", message


def display_input(
    message: str, history: list[tuple[str, str]]
) -> list[tuple[str, str]]:
    """
    Display the input message in the chat history.
    :param message: The input message.
    :param history: The chat history.
    :return: The chat history with the input message appended.
    """
    history.append((message, ""))
    return history


def delete_prev_fn(
        history: list[tuple[str, str]]) -> tuple[list[tuple[str, str]], str]:
    """
    Delete the previous message from the chat history.
    :param history: The chat history.
    :return: The chat history with the last message removed
    and the removed message.
    """
    try:
        message, _ = history.pop()
    except IndexError:
        message = ""
    return history, message or ""


def generate(
    message: str,
    history_with_input: list[tuple[str, str]],
    system_prompt: str,
    max_new_tokens: int,
    temperature: float,
    top_p: float,
    top_k: int,
) -> Iterator[list[tuple[str, str]]]:
    """
    Generate a response to the input message.
    :param message: The input message.
    :param history_with_input: The chat history with
    the input message appended.
    :param system_prompt: The system prompt.
    :param max_new_tokens: The maximum number of tokens to generate.
    :param temperature: The temperature.
    :param top_p: The top-p (nucleus sampling) probability.
    :param top_k: The top-k probability.
    :return: An iterator over the chat history with
    the generated response appended.
    """
    if max_new_tokens > MAX_MAX_NEW_TOKENS:
        raise ValueError

    history = history_with_input[:-1]
    generator = run(
        message, history,
        system_prompt, max_new_tokens, temperature, top_p, top_k
    )
    try:
        first_response = next(generator)
        yield history + [(message, first_response)]
    except StopIteration:
        yield history + [(message, "")]
    for response in generator:
        yield history + [(message, response)]


def process_example(message: str) -> tuple[str, list[tuple[str, str]]]:
    """
    Process an example.
    :param message: The input message.
    :return: A tuple of the empty string and the chat history with the \
        generated response appended.
    """
    generator = generate(message, [], DEFAULT_SYSTEM_PROMPT, 1024, 1, 0.95, 50)
    for x in generator:
        pass
    return "", x


def check_input_token_length(
    message: str, chat_history: list[tuple[str, str]], system_prompt: str
) -> None:
    """
    Check that the accumulated input is not too long.
    :param message: The input message.
    :param chat_history: The chat history.
    :param system_prompt: The system prompt.
    :return: None.
    """
    input_token_length = len(message) + len(chat_history)
    if input_token_length > MAX_INPUT_TOKEN_LENGTH:
        raise gr.Error(
            f"The accumulated input is too long \
            ({input_token_length} > {MAX_INPUT_TOKEN_LENGTH}).\
            Clear your chat history and try again."
        )


with gr.Blocks(css="./styles/style.css") as demo:
    gr.Markdown(DESCRIPTION)
    gr.DuplicateButton(
        value="Duplicate Space for private use", elem_id="duplicate-button"
    )

    with gr.Group():
        chatbot = gr.Chatbot(label="Playground")
        with gr.Row():
            textbox = gr.Textbox(
                container=False,
                show_label=False,
                placeholder="Hi, Mistral!",
                scale=10,
            )
            submit_button = gr.Button("Submit", variant="primary",
                                      scale=1, min_width=0)
    with gr.Row():
        retry_button = gr.Button('🔄  Retry', variant='secondary')
        undo_button = gr.Button('↩️ Undo', variant='secondary')
        clear_button = gr.Button('🗑️  Clear', variant='secondary')

    saved_input = gr.State()

    with gr.Accordion(label="⚙️ Advanced options", open=False):
        system_prompt = gr.Textbox(
            label="System prompt",
            value=DEFAULT_SYSTEM_PROMPT,
            lines=5,
            interactive=False,
        )
        max_new_tokens = gr.Slider(
            label="Max new tokens",
            minimum=1,
            maximum=MAX_MAX_NEW_TOKENS,
            step=1,
            value=DEFAULT_MAX_NEW_TOKENS,
        )
        temperature = gr.Slider(
            label="Temperature",
            minimum=0.1,
            maximum=4.0,
            step=0.1,
            value=0.1,
        )
        top_p = gr.Slider(
            label="Top-p (nucleus sampling)",
            minimum=0.05,
            maximum=1.0,
            step=0.05,
            value=0.9,
        )
        top_k = gr.Slider(
            label="Top-k",
            minimum=1,
            maximum=1000,
            step=1,
            value=10,
        )

    textbox.submit(
        fn=clear_and_save_textbox,
        inputs=textbox,
        outputs=[textbox, saved_input],
        api_name=False,
        queue=False,
    ).then(
        fn=display_input,
        inputs=[saved_input, chatbot],
        outputs=chatbot,
        api_name=False,
        queue=False,
    ).then(
        fn=check_input_token_length,
        inputs=[saved_input, chatbot, system_prompt],
        api_name=False,
        queue=False,
    ).success(
        fn=generate,
        inputs=[
            saved_input,
            chatbot,
            system_prompt,
            max_new_tokens,
            temperature,
            top_p,
            top_k,
        ],
        outputs=chatbot,
        api_name=False,
    )

    button_event_preprocess = (
        submit_button.click(
            fn=clear_and_save_textbox,
            inputs=textbox,
            outputs=[textbox, saved_input],
            api_name=False,
            queue=False,
        )
        .then(
            fn=display_input,
            inputs=[saved_input, chatbot],
            outputs=chatbot,
            api_name=False,
            queue=False,
        )
        .then(
            fn=check_input_token_length,
            inputs=[saved_input, chatbot, system_prompt],
            api_name=False,
            queue=False,
        )
        .success(
            fn=generate,
            inputs=[
                saved_input,
                chatbot,
                system_prompt,
                max_new_tokens,
                temperature,
                top_p,
                top_k,
            ],
            outputs=chatbot,
            api_name=False,
        )
    )

    retry_button.click(
        fn=delete_prev_fn,
        inputs=chatbot,
        outputs=[chatbot, saved_input],
        api_name=False,
        queue=False,
    ).then(
        fn=display_input,
        inputs=[saved_input, chatbot],
        outputs=chatbot,
        api_name=False,
        queue=False,
    ).then(
        fn=generate,
        inputs=[
            saved_input,
            chatbot,
            system_prompt,
            max_new_tokens,
            temperature,
            top_p,
            top_k,
        ],
        outputs=chatbot,
        api_name=False,
    )

    undo_button.click(
        fn=delete_prev_fn,
        inputs=chatbot,
        outputs=[chatbot, saved_input],
        api_name=False,
        queue=False,
    ).then(
        fn=lambda x: x,
        inputs=[saved_input],
        outputs=textbox,
        api_name=False,
        queue=False,
    )

    clear_button.click(
        fn=lambda: ([], ""),
        outputs=[chatbot, saved_input],
        queue=False,
        api_name=False,
    )

demo.queue(max_size=32).launch(share=HF_PUBLIC, show_api=False)