---
title: Some facts about accessing LLM models
date: 2026-09-27
category: cs
---

Nearly 9 out of 10 companies in US have integrated AI at an enterprise level. There are two ways for companies to get access to LLM models at an enterprise level (obviously any individual employee can use AI with her personal account, but that's not really the topic to be discussed in this blog). 

## Cloud API

Most AI companies have enterprise subscription plans that give corporates licenses to use their model. Verifified corporate accounts can then access LLM models like an individual would: send API requests (don't know what this is? check out my other blog!) to the AI company's servers, where the LLM models live. This is referred to as connecting to LLM via cloud API. I heard from a friend that his company connected their own product sorting software to an **Optical Character Recognition (OCR)** model to scan the strings on barcodes. 

It is reported that 80% of the aforementioned corporates in US use cloud API. In contrast to individual use, the data sent to the LLM Enterprise-Grade APIs are kept confidential by law (and encryption), so AI companies can't see or use the data to train their models. 

## Local deployment. 

Another way for corporates to use LLM is to deploy them on the company servers. Some LLM are open source. Companies find and download model weights (neural network's parameters) and configuration files from hubs like Hugging Face. These data are loaded into the specialized memory of linked GPUs, and using a lightweight software engine to instantly run text through that memory to calculate and generate responses. 

Employees usually have to be connected to the company intranet in order to access the servers, and hence the LLM. An **intranet** is a private, secure computer network that allows people within a specific organization to communicate, share information, and work together. It's not too urgent to dig into intranets. 


The company that I did my internship at deployed a deepseek and a GLM model. They used a tool called CC switch to redirect the local request endpoints of tools like Claude Code to their internal, self-hosted LLM gateway. Let me explain what this means. 

Claude Code is the CLI/application. Claude does not necessarily have to be the model underneath it. Apps like CC switch is just an editor for changing the global environment variables and settings of Claude Code. Specifically, CC Switch is changing the server that Claude Code talks to. Many third-party models expose an API that is compatible with Anthropic's API format, so Claude Code can send requests to them as if it were talking to Claude. CC Switch maps Claude Code's abstract model names such as Haiku/Sonnet/Opus to actual models from another provider. 

## Issues that could arise with accessing CLI-based agents


Terminals (translators between your commands and the system's operating system) also need an environment like any software does (building a software without an environment is like building a house without a location, not knowing where materials come from, and what it should look like). 

The .zshrc is a configuration file that customizes the Z shell (Zsh) environment every time you open an interactive terminal session. Back when I was doing an internship where I had to access the company's private server, CC switch edited my .zshrc file and added `export HTTPS_PROXY = "..."` which creates an environment variable that forces your terminal and command-line programs to route all secure web traffic to a specific intermediary proxy server that points to the company's private servers. This is what I meant by "changing the server that Claude Code talks to" three paragraphs ago. Deleteing those lines should solve the issue of "API error" or "Connection refused ..." when talking to claude code. 








