---
title: On IDE, git, and workflow (To be updated)
date: 2026-08-24
category: cs
---

This note aims to introduce basic knowledge and tips about things related to using VS Code, git, and workflow incorporated with AI. The aim is to help beginners in programming feel less overwhelmed by the technical details involved in coding. This short blog will tell you how to run a piece of code with VS Code and how your computer actually makes it work. Only the important technical details are mentioned. 

I use visual studio code, which is an Integrated Development Environment (IDE). It handles editing, building, testing, and packaging of codes. An IDE can do the job of an editor, but much more. As of 2026, VSCode remains a popular choice for IDE and I find it quite delightful to work with. 

`cmd+o` to select a folder that you want to work within. You can view and edit files, which is not surprising since VS Code is at minimum an *editor*. 

When you open a terminal session, the shell (zsh or bash) by default sets the PATH variable to be something like /usr/bin:/bin:/usr/sbin:/sbin. PATH is a list of "address" (stored in memory, not an actual file) separated by colons that the shell will search into when you tell it to executed a program. 

The shell also needs a working directory specified. The shell can only access files below the working directory. 

When you run a .py file, VS Code will ask you to choose a python interpreter. The interpreter is a program that translate the high-level(meaning close to human language) code, line by line, to machine code that your computer can understand. Your computer likely has a globally installed python interpreter(it's meant to be for quick, non-project-specific usage). If you choose that global PATH, then VS Code lets your terminal proceed to run the file. Python interpreter lives together with packages(such as pandas) that the user installed in the past.  Together they are called environment. But sometimes different projects need different version of the same package, so people may want to have an environment stored in a specific folder to indicate it is for a specific project. This resolves potential package conflicts. This is called a virtual environment. When you select the virtual environment when prompted by VS Code, VS Code puts the path of the virtual python interpreter at the front of the PATH. This way, when you run a .py file or python3, the shell reaches that virtual interpreter first instead of the global interpreter. 


To kill this terminal, you can use the trash icon on the upper right or run `exit`. If you want to get the terminal out of your sight but may need it later, close it using the X icon. If you don't kill a terminal, it continues to consume memory (RAM, specifically). 
