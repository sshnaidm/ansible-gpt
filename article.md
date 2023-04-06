# Ansible GPT - callback plugin with OpenAI for Ansible tasks and playbooks

![Ansible GPT Demo](https://github.com/sshnaidm/ansible-gpt/raw/master/openai-callback-demo.gif)

With the recent hype around GPT, there have been many successful (and not so successful) attempts to generate Ansible or Terraform playbooks. However, I would like to suggest another potential use for OpenAI: the explanation and improvement of the current playbooks and tasks that we use.

Ansible offers more than just running tasks and executing commands, it includes a variety of useful features such as plugins and modules. One such feature is callback plugins, which can be configured to respond to each task and playbook execution with customized actions. They can provide valuable insights into the execution of Ansible playbooks and offer a way to extend Ansible's functionality by allowing custom behavior and output handling.

In this blog post, we will introduce an Ansible callback plugin that leverages the power of OpenAI's natural language processing capabilities. This plugin provides detailed explanations and recommendations for improving Ansible tasks. Notably, the plugin offers insights not just for individual tasks, but it also provides an overview of the entire playbook, its purpose, and its functionality. During the Ansible run, the explanations and suggestions are posted before each task and playbook, making it easier for users to understand the execution and identify areas that could be improved.

It doesn't make sense to run the plugin during every playbook execution if nothing has changed in the playbook. Therefore, it's better for the user to specify the callback in the command line only when it's required. Additionally, you can configure its enablement and various options via environment variables or the Ansible configuration file.

To start with the installation process, you need to install the Ansible collection from Galaxy, which includes this plugin (and potentially other useful tools in the future).
```
ansible-galaxy collection install sshnaidm.openai
```

The collection is published in Ansible Galaxy as [sshnaidm.openai](https://galaxy.ansible.com/sshnaidm/openai) and sources are in Github repository [https://github.com/sshnaidm/ansible-gpt](https://github.com/sshnaidm/ansible-gpt)

The only required parameter for running the OpenAI callback plugin is the OpenAI API key, which can be generated on the OpenAI website at https://platform.openai.com/account/api-keys. If you don't have an account yet, you will need to set one up. Once you have the API key, you can either set it in the Ansible configuration file (usually located at ~/.ansible.cfg) or in the environment variable OPENAI_API_KEY, like so: export OPENAI_API_KEY=<my-key>.

The remaining parameters are optional and can be configured according to your needs:

* openai_model - by default `gpt-3.5-turbo` is used (could be set with environment variable `OPENAI_MODEL`)
* temperature_ai - AI temperature, you can read more about it in [OpenAI docs](https://platform.openai.com/docs/api-reference/completions/create#completions/create-temperature) (could be set with environment variable `OPENAI_TEMPERATURE`), by default it's set in OpenAI.
* tokens_ai - AI max tokens, you can read more about it in [OpenAI docs](https://platform.openai.com/docs/api-reference/completions/create#completions/create-max_tokens) (could be set with environment variable `OPENAI_TOKENS`), by default it's set in OpenAI.

All of these parameters can be configured in the Ansible configuration file (`ansible.cfg`). For example:

```INI
[defaults]
# .... here goes my other settings
[callback_openai]
openai_api_key="<my-key>"
openai_model="gpt-4"
temperature_ai="0.8"
tokens_ai="2048"
```

The OpenAI callback plugin shouldn't run with every playbook execution, which is why it needs to be enabled in the list of plugins. If you want to run it always, you can enable it in the `callbacks_enabled` section of the configuration file, like so:

```INI
[defaults]
stdout_callback = ansible.posix.debug
callbacks_enabled = profile_tasks,sshnaidm.openai.openai
```

However, it's important to note that this can quickly exhaust your OpenAI account's resources, so it's recommended to enable the plugin only for specific Ansible playbook runs. This can be done easily with environment variables. For example, to enable the OpenAI callback plugin for a single playbook run, set `ANSIBLE_CALLBACKS_ENABLED=sshnaidm.openai.openai` before running the Ansible command:

```bash
ANSIBLE_CALLBACKS_ENABLED=sshnaidm.openai.openai ansible-playbook -vv playbook.yml -i localhost,
```

If you have multiple plugins to enable, separate them with a comma, like so: `ANSIBLE_CALLBACKS_ENABLED=profile_tasks,sshnaidm.openai.openai ansible-playbook -vv playbook.yml -i localhost,`

Please pay attention: AI recommendations do NOT always make sense. You can adjust the temperature to get more or less conservative suggestions, but it's still up to humans to understand and evaluate the suggestions as acceptable or ridiculous. Don't worry, the AI won't take your job unless you blindly accept everything it tells you. Only then you might not be needed anymore :D

The callback plugin is developed in Github repository https://github.com/sshnaidm/ansible-gpt and your feedback is very welcome. Please feel free to submit any issues or patches.

## How to write your own Ansible Callback plugin?

More about callback plugins: https://docs.ansible.com/ansible/latest/plugins/callback.html

Ansible Callback plugins serve as triggers for various actions during the course of running an Ansible playbook. These actions can include starting a task, ending a playbook, or detecting a failure or change in a task. You can find the complete list of possible events that you can use in your callback plugin on this GitHub repository: https://github.com/ansible/ansible/blob/devel/lib/ansible/plugins/callback/__init__.py. You should look for events that start with "v2_" since those are the ones that are currently supported.

Typically, you create a callback class that inherits from the "CallbackBase" class and then implement the methods you want to use. For example, if you want to send an HTTP message on a task failure, you would use the "v2_runner_on_failed" method. Here's an example implementation:

```python
class MyCallbackPlugin:
    def v2_runner_on_failed(self, result, ignore_errors=False):
        if ignore_errors:
            return
        send_to_url_failed_result_data(result)
```

Callback plugins can receive configuration options, which are typically passed via environment variables or the Ansible configuration file (ansible.cfg). For instance, in my OpenAI callback plugin, there's an option for an API key:

```yaml
options:
      openai_api_key:
        description: OpenAI API key
        env:
          - name: OPENAI_API_KEY
        ini:
          - section: callback_openai
            key: openai_api_key
```

This means that you can set the "openai_api_key" parameter using either the OPENAI_API_KEY environment variable or by adding it to the "callback_openai" section in an Ansible configuration file (in INI format) like so:

```ini
[defaults]
...
[callback_openai]
openai_api_key="<my-key>"
```

It's best to group all the options for your plugin under the same section in the configuration file.

You can find all the currently available callback plugins for Ansible in this list: https://docs.ansible.com/ansible/latest/collections/index_callback.html. This is an excellent resource for learning how to write your own callback plugins, as you can examine the examples provided by the existing plugins.
