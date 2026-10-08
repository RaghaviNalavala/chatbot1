from __future__ import annotations

import json
import os
from typing import Any

import requests
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://localhost:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'qwen2.5:3b')

SYSTEM_PROMPT = """
You are a helpful career guidance assistant and general advisor.
Answer user questions in a friendly, clear, and encouraging tone.

Your abilities:
- Career guidance: study pathways, college choices, jobs, skills, resume, interviews, and career planning.
- Education guidance: school subjects, exam prep, choosing streams, time management, and learning strategies.
- Games: discuss game choices, game design, gameplay improvements, gaming time balance, and esports/tech careers.
- Medical assistance: give safe general health guidance, basic first-aid info, wellness tips, and explain when to consult a doctor.
- Also answer other general questions in a helpful way.

Important safety rules:
- Never claim to be a doctor.
- For emergencies or serious symptoms, advise immediate medical attention from a qualified professional.
- Keep support practical and non-judgmental.
- If a request is not clear, ask follow-up questions.
"""


@app.get('/')
def index():
    return render_template('index.html')


@app.post('/api/chat')
def chat():
    payload = request.get_json(silent=True) or {}
    user_message = (payload.get('message') or '').strip()

    if not user_message:
        return jsonify({'error': 'Please enter a message.'}), 400

    try:
        response = requests.post(
            f'{OLLAMA_URL}/api/chat',
            json={
                'model': OLLAMA_MODEL,
                'messages': [
                    {'role': 'system', 'content': SYSTEM_PROMPT},
                    {'role': 'user', 'content': user_message},
                ],
                'stream': False,
                'options': {'temperature': 0.7},
            },
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()
        reply = data.get('message', {}).get('content', '').strip()

        if not reply:
            raise ValueError('The model returned an empty response.')

        return jsonify({'reply': reply})

    except requests.exceptions.RequestException as exc:
        return jsonify({
            'reply': (
                f'I could not reach Ollama at {OLLAMA_URL}. Please make sure Ollama is running and the "{OLLAMA_MODEL}" model is available.'
            )
        }), 200
    except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        return jsonify({
            'reply': f'I am here, but the model response was not usable. Please try again. Details: {exc}'
        }), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
