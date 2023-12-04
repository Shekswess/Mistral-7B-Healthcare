---
title: Mistral 7B Healthcare
emoji: 😻
colorFrom: yellow
colorTo: yellow
sdk: gradio
sdk_version: 3.50.2
app_file: app.py
models:
  - mistralai/Mistral-7B-v0.1
  - mistralai/Mistral-7B-Instruct-v0.1
pinned: false
license: mit
---

# Mistral-7B-Healthcare

This is an implementation of pretrained Mistral-7B model for Healthcare domain. It is deployed using Gradio on HuggingFace Spaces. The main purpose of this model is to provide a quick way to show the capabilities of Mistral-7B model on Healthcare/Wellness/Medical domain, and to provide a quick way to test the model on providing context for Healthcare and Wellness. It can be used to generate outputs using outputs from other models typicaly used in these domains(as Human Activity Recognition-HAR models) as inputs to the Mistral-7B model LLM.

## How to use

The deployed model can be accessed at [https://huggingface.co/spaces/Shekswess/Mistral-7B-Healthcare](https://huggingface.co/spaces/Shekswess/Mistral-7B-Healthcare).

1. Enter the structured text in the input box.
2. Click on the `Submit` button.
3. The output will be generated in the output box.

## How to deploy your own model on HuggingFace Spaces

1. Fork this repository.
2. Go to [https://huggingface.co/spaces/new](https://huggingface.co/spaces/new).
3. Create a new space(you can name it anything you want).
4. Create secret tokens for your space on HuggingFace Spaces.
5. Create secret tokens on the forked repository on GitHub.
6. Change the deploy workflow file to use your secret tokens and space name.
7. Commit the changes and push to the forked repository to the `main` branch to trigger the workflow.

## Requirements

To use the code you need:
- Python >= 3.9

To install the requirements run the following command:
```
pip install -r requirements.txt
```

## Structure

The structure of the repository is:
```
.
├── .github/workflows           # Contains the workflow file for deployment
│   └── deploy.yml              # Workflow file for deployment    
├── src                         # Contains the source code
│   ├── model.py                # Contains the code for the model
├── styles                      # Contains the styles for the web app
│   └── style.css               # The css file for the web app
├── .gitignore                  # Contains the files to be ignored by git
├── app.py                      # Contains the code for the web app
├── README.md                   # Contains the README file
└── requirements.txt            # Contains the requirements for the code
```