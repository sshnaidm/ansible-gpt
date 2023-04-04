# -*- coding: utf-8 -*-
# Copyright (c) 2023 Sagi Shnaidman <sshnaidm@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


DOCUMENTATION = '''
    name: openai
    type: stdout
    short_description: Analyzes Ansible tasks and playbooks with OpenAI GPT
    description:
      - Analyzes Ansible tasks and playbooks with OpenAI GPT
      - Prints explanations for the tasks and playbooks
      - Suggests improvements to the tasks and playbooks if any
    requirements:
      - enable in configuration - see examples section below for details.

    options:
      openai_api_key:
        description: OpenAI API key
        env:
          - name: OPENAI_API_KEY
        ini:
          - section: callback_openai
            key: openai_api_key
      openai_model:
        description: OpenAI model
        default: gpt-3.5-turbo
        env:
          - name: OPENAI_MODEL
        ini:
          - section: callback_openai
            key: openai_model
      temperature_ai:
        description: Temperature for OpenAI GPT
        env:
          - name: OPENAI_TEMPERATURE
        ini:
          - section: callback_openai
            key: openai_temperature
      tokens_ai:
        description: Number of tokens for OpenAI GPT
        env:
          - name: OPENAI_TOKENS
        ini:
          - section: callback_openai
            key: openai_tokens
'''


import json  # noqa: E402
import yaml  # noqa: E402
try:
    import openai  # noqa: E402
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

from ansible.plugins.callback import CallbackBase  # noqa: E402
from ansible.module_utils._text import to_text  # noqa: E402


def get_openai_description(
        task_text=None,
        play_text=None,
        temperature_ai=None,
        tokens_ai=None,
        openapi_key=None,
        model=None):
    if not HAS_OPENAI:
        return to_text("Please install openai python library to use this plugin")
    openai.api_key = openapi_key
    if not openapi_key:
        return to_text("Please set OPENAI_API_KEY environment variable for GPT plugin to work. "
                "Either in the environment OPENAI_API_KEY or in the config file.")
    kwargs = {'model': model}
    if temperature_ai:
        kwargs['temperature'] = float(temperature_ai)
    if tokens_ai:
        kwargs['max_tokens'] = int(tokens_ai)
    if task_text:
        prompt = ("Explain what this Ansible task does, "
                  "don't print the task itself, only explanation:"
                  f"\n```\n{task_text}```\n"
                  "If you have any significant improvements for this task, "
                  "please suggest them as well, print them after word 'Suggestions:'"
                  "If you don't have any suggestions, print 'No suggestions'.")
    elif play_text:
        prompt = ("Explain what this Ansible playbook does, "
                  "focus on the whole purpose of the playbook, rather than on the tasks."
                  "Don't print the playbook itself, only explanation:"
                  f"\n```\n{play_text}```\n"
                  "If you have any significant improvements for this task, "
                  "please suggest them as well, print them after word 'Suggestions:'"
                  "If you don't have any suggestions, print 'No suggestions'.")

    kwargs['messages'] = [
        {"role": "system",
                 "content": "You are a helpful assistant and Ansible expert. :)"},
        {"role": "assistant", "content": ""},
        {"role": "user", "content": prompt},
    ]
    try:
        response = openai.ChatCompletion.create(**kwargs)
    except Exception as e:
        return to_text(f"Error: {e}")
    if response.choices:
        if 'text' in response.choices[0]:
            answer = response.choices[0].text.strip()
        else:
            answer = response.choices[0].message.content.strip()
    else:
        answer = "No answer from OpenAI!"
    return to_text(answer)


class CallbackModule(CallbackBase):

    CALLBACK_VERSION = 1.0
    CALLBACK_TYPE = 'aggregate'
    CALLBACK_NAME = 'sshnaidm.openai.openai'
    CALLBACK_NEEDS_WHITELIST = True

    def __init__(self):
        super(CallbackModule, self).__init__()
        self.model = None
        self.temperature_ai = None
        self.tokens_ai = None
        self.openapi_key = None
        self.kwargs = None

    def set_options(self, task_keys=None, var_options=None, direct=None):
        super(CallbackModule, self).set_options(task_keys=task_keys,
                                                var_options=var_options,
                                                direct=direct)
        self.model = self.get_option('openai_model')
        self.temperature_ai = self.get_option('temperature_ai')
        self.tokens_ai = self.get_option('tokens_ai')
        self.openapi_key = self.get_option('openai_api_key')
        self.kwargs = {
            'model': self.model,
            'openapi_key': self.openapi_key,
            'temperature_ai': self.temperature_ai,
            'tokens_ai': self.tokens_ai
        }

    def v2_playbook_on_task_start(self, task, is_conditional):
        task_text = yaml.dump([json.loads(json.dumps(task._ds))])
        kwargs = {'task_text': task_text, **self.kwargs}
        print(f"Explanation: \n{get_openai_description(**kwargs)}")

    def v2_playbook_on_play_start(self, play):
        play_text = yaml.dump(json.loads(json.dumps(play.get_ds())))
        kwargs = {'play_text': play_text, **self.kwargs}
        print(f"Explanation: \n{get_openai_description(**kwargs)}")
