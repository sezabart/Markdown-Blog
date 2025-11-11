"""Small helper utilities to centralize config-derived paths and common helpers.

This module is intentionally tiny and low-risk. It reads the in-memory config values from
`make_app` (which already loads `config.yaml`) and exposes path helpers that other modules
can import gradually.
"""
from pathlib import Path
from make_app import blogs_config, content_dir, landing_config


def get_blogs_config():
    return blogs_config


def get_landing_config():
    return landing_config


def mailing_list_path(blog: str) -> Path:
    """Return path to the mailing list file for `blog` (mailing_lists/<blog>.txt).
    Caller is responsible for creating directory if needed.
    """
    ml_dir = Path("mailing_lists")
    ml_dir.mkdir(exist_ok=True)
    return ml_dir / f"{blog}.txt"


def mail_lock_path(blog: str, post_name: str) -> Path:
    lock_dir = Path("mail_locks")
    lock_dir.mkdir(exist_ok=True)
    return lock_dir / f"{blog}--{post_name}.lock"


def last_sent_path(blog: str, post_name: str) -> Path:
    meta_dir = Path("mail_meta")
    meta_dir.mkdir(exist_ok=True)
    return meta_dir / f"{blog}--{post_name}.json"
