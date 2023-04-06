# Ansible-GPT ansible-lint rule - OpenAI inspecting tool for Ansible tasks and playbooks

![Ansible GPT linter Demo](https://github.com/sshnaidm/ansible-gpt/raw/master/openai-lintrule-demo.gif)

If you want inspect your Ansible code with OpenAI, just run the following commands:

```bash
pip install openai ansible-lint
export OPENAI_API_KEY=<my-key>
git clone https://github.com/sshnaidm/ansible-gpt.git
ansible-lint -v -r ansible-gpt/ansible_lint/rules/ --project-dir /path/to/my_project /path/to/my_project/playbook.yml
```

And for those who want to write their own Ansible-lint rules, let's start!

[Ansible lint](https://github.com/ansible/ansible-lint) is a super handy tool that helps you find syntax errors in your Ansible code and makes sure your tasks and playbooks are following best practices. It checks your code against a bunch of rules and you can even create your own and run them. It's like having your own personal code inspector for Ansible.
So, let's take advantage of that tool and use it to inspect our Ansible code with OpenAI, writing our own AI based rule.
Ansible lint comes with documentation and [pre-built rules](https://github.com/ansible/ansible-lint/tree/main/src/ansiblelint/rules) that we can use as examples to learn from. It has different levels of checks - for tasks, YAML files (whole files), playbooks, and roles. Since we can analyze any Ansible code with OpenAI, let's focus on the YAML files and send the whole content for analysis. This will give OpenAI more context to work with and improve the inspection results.

Let's start with the basics and define a general rule:

```python
from ansiblelint.rules import AnsibleLintRule

class OpenAISuggestion(AnsibleLintRule):
    """Get suggestion about your Ansible code from OpenAI."""

    id = "openai-input"
    description = "Suggestions from OpenAI"
    severity = "VERY_LOW"
    tags = ["productivity", "experimental"]
    version_added = "historic"

```

We imported the AnsibleLintRule from the installer ansible-lint package and created a class that inherits from it. There are a few parameters worth specifying, like "id", "description", and so on.
Next, we need to decide what we are going to inspect - a task, playbook, role, etc. Let's assume it's a task and use the `matchtask` method:

```python
def matchtask(self, task, file):
    return False
```

If the rule detects a failure, it should return specific results with explanations or just "True" if it's clear why it fails. For example, let's fail the rule if we have a "shell" task and "ignore_errors" specified:

```python
def matchtask(self, task, file):
    return task["action"]["__ansible_module__"] in ("shell", "ansible.builtin.shell") and task.get("ignore_errors")
```

If we'd like to include more data about the failure or, like in our case with OpenAI, provide a whole explanation and suggestions, we can use the `self.create_matcherror` method, for example:

```python

def matchtask(self, task, file):
    matches = []
    # ... some checks ....
    matcherror = self.create_matcherror(
        message="A brief message explaining what is going on",
        linenumber=<optional line number where we hit the issue>,
        details="And here comes all information that we want to provide to user",
        filename=<optional file name>,
    )
    matches.append(matcherror)
    return matches
```

To run this rule only we can use `-r` option with path to our rules directory. If we need to include all other default rules, we can add `-R` parameter. Also it's important to specify the project directory with `--project-directory` argument if it's not the current directory. Let's run our rule now:

```bash
ansible-lint -v -r ansible_lint/rules/ --project-dir /path/to/my_project /path/to/my_project/playbook.yml
```

Results are printed in the terminal. Happy linting!
