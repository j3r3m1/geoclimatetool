# -*- coding: utf-8 -*-

"""
Downloads folders from github repo
Requires PyGithub
Code adapted from https://gist.github.com/pdashford/2e4bcd4fc2343e2fd03efe4da17f577d
@author: Jérémy Bernard, CNRM, chercheur associé au Lab-STICC et accueilli au LOCIE
"""

import base64
import getopt
import os
import shutil
import sys
from typing import Optional

from github import Github, GithubException
from github.ContentFile import ContentFile
from github.Repository import Repository


def get_sha_for_tag(repository: Repository, tag: str) -> str:
    """
    Returns a commit PyGithub object for the specified repository and tag.
    """
    branches = repository.get_branches()
    matched_branches = [match for match in branches if match.name == tag]
    if matched_branches:
        return matched_branches[0].commit.sha

    tags = repository.get_tags()
    matched_tags = [match for match in tags if match.name == tag]
    if not matched_tags:
        raise ValueError("No Tag or Branch exists with that name")
    return matched_tags[0].commit.sha


def download_directory(repository: Repository, sha: str, server_path: str,
                       computer_dir: str) -> None:
    """
    Download all contents at server_path with commit tag sha in
    the repository.
    """
    if os.path.exists(server_path):
        shutil.rmtree(server_path)

    contents = repository.get_contents(server_path, ref=sha)

    for content in contents:
        print("Processing %s" % content.path)
        if content.type == "dir":
            os.makedirs(content.path)
            download_directory(repository, sha, content.path)
        else:
            try:
                path = content.path
                loc_dir = os.path.join(computer_dir, path.split("/")[-1])
                file_content = repository.get_contents(path, ref=sha)
                if not isinstance(file_content, ContentFile):
                    raise ValueError("Expected ContentFile")
                file_out = open(loc_dir, "w+")
                if file_content.content:
                    file_data = base64.b64decode(file_content.content)
                    file_out.write(file_data.decode("utf-8"))
                file_out.close()
            except (GithubException, IOError, ValueError) as exc:
                print("Error processing %s: %s", content.path, exc)