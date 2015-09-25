#!/usr/bin/env python

from setuptools import setup

setup(
        name            = "wp-release",
        version         = "0.1",
        author          = "Oliver Weissbarth",
        author_email    = "mail@oweissbarth.de",
        description     = ("wp-release is a tool to release wordpress plugins and themes. It was designed to work with 'YahnisElsts/plugin-update-checker' and 'YahnisElsts/theme-update'"),
        license         = "GPLv2",
        packages        = ["wp_release"],
        install_requires=["ConfigParser", "scp", "paramiko"],
        scripts         =["wp-release"]
        
)
