# Ansible GPT

OpenAI (GPT) additions for Ansible

## Callback plugin that analyzes the running playbook and tasks

More in [Article](https://github.com/sshnaidm/ansible-gpt/blob/master/article.md)
Usage:

```bash
pip install ansible-core openai
ansible-galaxy collection install sshnaidm.openai
export OPENAI_API_KEY=<my-key>
ANSIBLE_CALLBACKS_ENABLED=sshnaidm.openai.openai ansible-playbook playbook.yml
```

## Ansible-lint rule that checks tasks and playbooks and suggests improvements.

Usage:

```bash
pip install ansible-lint
git clone https://github.com/sshnaidm/ansible-gpt.git
ansible-lint -v -r ansible_lint/rules/ --project-dir /path/to/my_project /path/to/my_project/playbook.yml
```
