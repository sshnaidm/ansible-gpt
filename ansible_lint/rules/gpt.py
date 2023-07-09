from ansiblelint.rules import AnsibleLintRule

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
import os

if not HAS_OPENAI:
    raise Exception("Please install openai python library to use this plugin")

if not os.getenv("OPENAI_API_KEY"):
    raise Exception(
        "Please set OPENAI_API_KEY environment variable for GPT plugin to work. "
        "You can get it from https://platform.openai.com"
    )

openai.api_key = os.environ["OPENAI_API_KEY"]
MODEL = os.environ.get("OPENAI_MODEL", "gpt-4")
TEMPERATURE = os.environ.get("OPENAI_TEMPERATURE", "0.4")
TOKENS = os.environ.get("OPENAI_TOKENS")


def split_yaml(yaml_str, max_chunk_size=3800):
    chunks = []
    current_chunk = ""

    for line in yaml_str.split("\n"):
        if len(current_chunk + line) > max_chunk_size:
            chunks.append(current_chunk)
            current_chunk = ""
        current_chunk += line + "\n"

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def clean_yaml(yaml_str):
    """This function removes all comments and empty lines from YAML string."""
    cleaned = []
    for line in yaml_str.split("\n"):
        if line.strip() and not line.strip().startswith("#"):
            cleaned.append(line)
    return "\n".join(cleaned)


class OpenAISuggestion(AnsibleLintRule):
    """Get suggestion about your Ansible code from OpenAI."""

    id = "openai-input"
    description = "Suggestions from OpenAI"
    severity = "VERY_LOW"
    tags = ["productivity", "experimental"]
    version_added = "historic"
    _kwargs = {"model": MODEL}

    def matchyaml(self, file):
        results = []

        content = file._content
        content = clean_yaml(content)
        prompt = (
            "I want you to act as a code reviewer for Ansible, and provide feedback on potential"
            "improvements to the code. As a reviewer, I expect you to analyze the code for best practices,"
            "identify any potential issues or inefficiencies,"
            "and suggest improvements to optimize performance and readability. Here is my code:"
            f"\n```\n{content}```\n"
            "Explain briefly what current Ansible code does, don't print the code itself."
            "If you have any significant improvements for this code, "
            "please suggest them as well, print them after word 'Suggestions:'"
            "If you don't have any suggestions, print 'No suggestions' only."
        )
        if TEMPERATURE:
            self._kwargs["temperature"] = float(TEMPERATURE)
        if TOKENS:
            self._kwargs["max_tokens"] = int(TOKENS)
        self._kwargs["messages"] = [
            {"role": "system", "content": "You are a helpful assistant and code reviewer for Ansible. :)"},
            {"role": "assistant", "content": ""},
            {"role": "user", "content": prompt},
        ]
        if len(content) > 3800:
            chunks = split_yaml(content)
        else:
            chunks = [content]
        for chunk in chunks:
            self._kwargs["messages"][2]["content"] = (
                "I want you to act as a code reviewer for Ansible, and provide feedback on potential"
                "improvements to the code. As a reviewer, I expect you to analyze the code for best practices,"
                "identify any potential issues or inefficiencies,"
                "and suggest improvements to optimize performance and readability. Here is my code:"
                f"\n```\n{chunk}```\n"
                "Explain briefly what current Ansible code does, don't print the code itself."
                "If you have any significant improvements for this code, "
                "please suggest them as well, print them after word 'Suggestions:'"
                "If you don't have any suggestions, print 'No suggestions' only."
            )
            try:
                response = openai.ChatCompletion.create(**self._kwargs)
            except Exception as e:
                return self.create_matcherror(
                    filename=file,
                    message=f"Exception while querying OpenAI: {e}",
                )
            if response.choices:
                if "text" in response.choices[0]:
                    answer = response.choices[0].text.strip()
                else:
                    answer = response.choices[0].message.content.strip()
            else:
                answer = "No answer from OpenAI!"
            match = self.create_matcherror(
                filename=file,
                message=f"{answer}",
            )
            match.level = "warning"
            results.append(match)

        return results
