# 🦄 Scoopika: Core

Build controllable AI-powered applications & agents.

NOTICE: This work is still under development.

NOTICE: This repository contains the core functionality of Scoopika, and it's not intended for use in application-level but for developers who want to build new open-source projects on top of it... If you're interested in using Scoopika in your application I recommend checking the [scoopika-py](https://github.com/scoopika/scoopika-py) for Python, or [scoopika-js](https://github.com/scoopika/scoopika-js) for Typescript.

## What is Scoopika ?

Scoopika is an ecosystem of tools for building controllable and predictable AI-powered applications around LLMs. applications that work with function-calling and agents.

Some of Scoopika's features:

1. Build context-aware applications that enable users to interact with their data in natural language.
2. Define rules and validation steps for the function calling process, your functions will NEVER receive inputs it does not expect again.
3. Create agents that do custom tasks easily in a minute.
4. Vector stores that provide history to the other parts of Scoopika, and works with any vector database you use.

## Run locally
You can run the core locally, first clone this repository and then install the requirements:
```bash
pip install -r requirements.txt
```

Now you can start using the core, it has a number of main classes: `ToolSelection` and `ArgumentsSelection`, and also the `prompts.dynamic` function for creating custom LLM prompts.

Again the core is not intended for application use, you can check how it works and figure out how to build on top of it, or configure it for your own use case.

The main Scoopika's functionality can be found in the main [scoopika-server](https://github.com/scoopika/scoopika) repository.

## Acknowledgement

We couldn't have done this project without all the effort the LangChain team have put in building their great open source project, a lot of functionalities in this core is built on top of their framework and we appreciate it (We are not affliated LangChain).

For all license notices we recommend you check the NOTICE file.

If you're an author of a work that this core depends on and you want us to add your name, citation, or license to the notice, please contact me on: kais.radwan.personal@gmail.com