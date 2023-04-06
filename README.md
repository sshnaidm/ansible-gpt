# Ansible GPT

OpenAI (GPT) additions for Ansible

## Callback plugin that analyzes the running playbook and tasks

Usage (more in [article](https://github.com/sshnaidm/ansible-gpt/blob/master/article.md)):

```bash
pip install ansible-core openai
ansible-galaxy collection install sshnaidm.openai
export OPENAI_API_KEY=<my-key>
ANSIBLE_CALLBACKS_ENABLED=sshnaidm.openai.openai ansible-playbook playbook.yml
```

## Ansible-lint rule that checks tasks and playbooks and suggests improvements

Usage (more in [article](https://github.com/sshnaidm/ansible-gpt/blob/master/article-lint.md)):

```bash
pip install openai ansible-lint
export OPENAI_API_KEY=<my-key>
git clone https://github.com/sshnaidm/ansible-gpt.git
ansible-lint -v -r ansible-gpt/ansible_lint/rules/ --project-dir /path/to/my_project /path/to/my_project/playbook.yml
```
