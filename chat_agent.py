from dataclasses import dataclass
from typing import List

from message import Message
from openai_operations import gpt_chat_completion


@dataclass
class ChatAgent:
    model: str = "gpt-3.5-turbo"
    system_prompt: str = None
    messages: List[Message] = None
    auto_summarize: int = 4
    auto_clear: bool = False
    verbose: bool = False
    tokens: str = None
    history_path: str = None

    def __post_init__(self):
        if not self.messages:
            self.messages = []
        if self.system_prompt:
            self.messages.append(Message('system', self.system_prompt))

    def submit(self, content):
        if self.verbose:
            print("ChatAgent.submit: ", content)

        # If tokens are provided, replace any {key} with the corresponding value
        # separated by a semicolon
        if self.tokens:
            for token in self.tokens.split(';'):
                key, value = token.split('=')
                content = content.replace("{{" + key + "}}", value)

        self.add_message('user', content)

        response = self.generate_response()

        return response

    def add_message(self, role, content):
        self.messages.append(Message(role, content))

    def generate_response(self):
        messages = [m.serialize() for m in self.messages]

        response = gpt_chat_completion(messages, model=self.model)

        if "maximum context length" in response:
            return response

        message = Message('assistant', response)
        self.add_message(message.role, message.content)

        if self.verbose:
            print(message.content)

        return message.content

    def get_user_messages(self):
        return [msg for msg in self.messages if msg.role == 'user']

    def __str__(self):
        return '\n'.join([f"{m.role}: {m.content}" for m in self.messages])

    def __len__(self):
        return len(self.messages)

    def __getitem__(self, index):
        return self.messages[index]
