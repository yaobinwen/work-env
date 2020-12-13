# Hamster

## Overview

`hamster` is a small tool that automatically checks if a specified Python code branch has new commits and, if so, builds and publishes the specified Python packages to the specified Python package server.

It does its job in the following steps repeatedly, similar to a hamster running on a wheel:
- Check if new commits are available.
- Test publishing
- Officially publish.
