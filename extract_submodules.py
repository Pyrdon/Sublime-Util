#!/usr/bin/env python3
"""
A script for unlinking all submodules and extracting their files.
"""

import logging

# Local logger
logger = logging.getLogger(__name__)

import os
import subprocess
import argparse
import logging
import shlex
import shutil
from pathlib import Path

def run_cmd(args : str, dry_run : bool = False, check : bool = True):
    """
    Runs a command

    :param args: The command as a string
    :param dry_run: Whether to just log the execution and not perform it
    :param check: Whether to check for errors or not
    """

    shlex_args = shlex.split(args)

    if dry_run:
        logger.debug(f"[dry-run] {' '.join(shlex_args)}")
        return

    logger.debug(' '.join(shlex_args))
    subprocess.run(shlex_args, check = check)

def get_submodules():
    """
    Get all submodules

    :returns: List of all submodules
    """

    logger.info("Getting submodules.")

    gitmodules = Path('.gitmodules')
    if not gitmodules.exists():
        return []

    lines = gitmodules.read_text().splitlines()
    submodules = []
    for line in lines:
        stripped_line = line.strip()
        if stripped_line.startswith('path = '):
            module = stripped_line.split(' = ', 1)[1].strip()
            logger.debug(f"Found submodule '{module}'.")
            submodules.append(module)
    return submodules

def remove_submodule_link(path: str, dry_run: bool):
    """
    Removes a linked submodule and its git meta data, but keeps all other files

    :param path: Submodule path
    :param dry_run: Whether to actually perform the removal or just perform a dry-run
    """

    logger.info(f"Removing submodule '{path}'.")
    run_cmd(f'git rm --cached {path}', dry_run)
    run_cmd(f'git config --remove-section submodule.{path}', dry_run, check = False)

    dot_git = Path(f"{path}/.git")
    if dot_git.exists():
        if dot_git.is_dir():
            if dry_run:
                logger.debug(f"[dry-run] Removing {dot_git} directory.")
            else:
                shutil.rmtree(dot_git)
        else:
            if dry_run:
                logger.debug(f"[dry-run] Removing {dot_git} file.")
            else:
                dot_git.unlink()

    run_cmd(f'git add {path}')

def cleanup_gitmodules(dry_run: bool):
    """
    Removing .gitmodules if exists

    :param dry_run: Whether to actually perform the removal or just perform a dry-run
    """

    gitmodules = Path('.gitmodules')
    if gitmodules.exists():
        if dry_run:
            logger.debug(f"[dry-run] Removing {gitmodules}.")
        else:
            run_cmd(f'git rm {gitmodules}')

def ensure_repo_root():
    """
    Moves to the root of the Git repository
    """

    repo_root = subprocess.run(
        ['git', 'rev-parse', '--show-toplevel'],
        capture_output = True, text = True, check = True
    ).stdout.strip()
    logger.debug(f"Moving to path {repo_root}.")
    os.chdir(repo_root)

def main():
    parser = argparse.ArgumentParser(
        description = "Extract Git submodules by removing links and keeping contents.")
    parser.add_argument('--dry-run', action = 'store_true', help = 'Preview actions without making changes')
    parser.add_argument('--verbose', '-v', action = 'store_true', help = 'Enable debug logging')
    args = parser.parse_args()

    logging.basicConfig(
        level = logging.DEBUG if args.verbose else logging.INFO,
        format = '[%(levelname)s] %(message)s'
    )

    ensure_repo_root()

    logger.info("Initializing submodules.")
    run_cmd('git submodule update --init --recursive', args.dry_run)

    submodules = get_submodules()
    if not submodules:
        logger.info("No submodules found.")
        return

    for submodule in submodules:
        remove_submodule_link(submodule, args.dry_run)

    cleanup_gitmodules(args.dry_run)

    logger.info("Done.")

if __name__ == "__main__":
    main()
