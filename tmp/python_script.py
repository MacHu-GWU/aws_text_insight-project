#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess

dir_project_root = "/Users/sanhehu/Documents/GitHub/aws_text_insight-project"
dir_venv_bin = "/Users/sanhehu/venvs/python/3.8.11/aws_text_insight_venv/bin"

# subprocess.run([f"{dir_venv_bin}/pip", "list"])
# subprocess.run(["virtualenv"])
# subprocess.run(["cd", ""])
# os.chdir(dir_project_root)
# subprocess.run(["make"])
subprocess.run(["aws", "s3", "ls", "--profile"])

