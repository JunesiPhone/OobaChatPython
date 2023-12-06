#!/usr/bin/env python
from datetime import datetime
from typing import List, Tuple
from uuid import uuid4
import requests
from nicegui import Client, ui
import asyncio

messages: List[Tuple[str, str, str, str]] = []

#oobabooga
url = "http://127.0.0.1:5000/v1/chat/completions"
headers = {"Content-Type": "application/json"}
history = []
data = {
            "mode": "chat",
            "character": "Example",
            "messages": history,
            "max_tokens": 250,
            "temperature": 0.7,
            "top_k": 20,
            "top_p": 0.9,
            "typical_p": 1,
            "min_p": 0,
            "top_a": 0,
            "repetition_penalty": 1.15,
            "presence_penalty": 0,
            "frequency_penalty": 0,
            "tfs": 1,
            "guidance_scale": 1,
            "mirostat_tau": 5,
            "mirostat_eta": 0.1,
            "use_ooba": True,
            "instruction_template": "Alpaca",
            "add_bos_token": True,
            "epsilon_cutoff": 0,
            "eta_cutoff": 0,
            "negative_prompt": '',
            "do_sample": True,
            "seed": -1,
            "encoder_repetition_penalty": 1,
            "no_repeat_ngram_size": 0,
            "min_length": 0,
            "num_beams": 1,
            "length_penalty": 1,
            "early_stopping": False,
            "truncation_length": 0,
            "max_tokens_second": 0,
            "custom_token_bans": "",
            "auto_max_new_tokens": False,
            "ban_eos_token": False,
            "skip_special_tokens": True,
            "grammar_string": "",
            "mode": "chat"
        }

def get_ai_response():
    response = requests.post(url, headers=headers, json=data, verify=False)
    if response:
        return response.json()['choices'][0]['message']['content']

@ui.refreshable
def chat_messages(own_id: str) -> None:
    for user_id, avatar, text, stamp in messages:
        time_12hr = stamp.strftime('%I:%M %p')
        chat_message = ui.chat_message(text=text, stamp=time_12hr, avatar=avatar, sent=own_id == user_id)
        if own_id == user_id:
            chat_message.props('text-color=black bg-color=white')
        else:
            chat_message.props('text-color=black bg-color=blue')
    ui.run_javascript('window.scrollTo(0, document.body.scrollHeight)')


@ui.page('/')
async def main(client: Client):
    async def send() -> None:
        ui.run_javascript('document.querySelector(".q-field__native").blur()')
        stamp = datetime.now()
        messages.append((user_id, avatar, text.value, stamp))
        history.append({"role": "user", "content": text.value})
        text.value = ''
        chat_messages.refresh()

        await asyncio.sleep(1)
        ai_response = get_ai_response()
        history.append({"role": "assistant", "content": ai_response})
        messages.append((ai_id, ai_avatar, ai_response, stamp))
        chat_messages.refresh()

    user_id = str(uuid4())
    avatar = f'https://robohash.org/{user_id}?bgset=bg2'

    ai_id = str(uuid4())
    ai_avatar = f'https://robohash.org/{ai_id}?bgset=bg2'

    anchor_style = r'a:link, a:visited {color: inherit !important; text-decoration: none; font-weight: 500}'
    chat_bubble_style = r'.q-message-sent{bg-color:red;}'
    ui.add_head_html(f'<style>{anchor_style}{chat_bubble_style}</style>')
    ui.add_head_html("<meta name='viewport' content='initial-scale=1, viewport-fit=cover, maximum-scale=1'>")
    ui.query('body').classes('bg-gray-600')
    with ui.footer().classes('bg-gray-600'), ui.column().classes('w-full max-w-3xl mx-auto my-6'):
        with ui.row().classes('w-full no-wrap items-center'):
            text = ui.input(placeholder='Type to chat').on('keydown.enter', send).props('rounded outlined input-class=mx-3 bg-color=white color=white').classes('flex-grow')
    await client.connected()  # chat_messages(...) uses run_javascript which is only possible after connecting
    with ui.column().classes('w-full max-w-2xl mx-auto items-stretch bg-gray-600'):
        chat_messages(user_id)

ui.run()
