wp-release
==========

wp-release is a tool to a new version of a wordpress theme or plugin to a server.
It was designed to work with YahnisElsts/plugin-update-checker and "theme-update" also by YahnisElsts.

wp-release extracts the current version-number from a given plugin or theme, creates a zip archive and uploads it to the server using ssh.
It then automatically updates the version number in the "<plugin/themename>.json"

**Please note:** The json file has to exist before.

Installation
-----------
Download the distributable from http://oweissbarth.de/download/984/

Run: `tar xvf wp-release-0.1.tar.gz` in the download directory to extract the tar
Run: `cd wp-release-0.1` to enter the extracted directory
Run: `python setup.py install` as root to install wp-release

Usage
------

To run wp-release just type: `wp-release <path-to-theme-or-plugin>` in the terminal.

It will ask you for some information regarding the server's ip and login info.
It will store all information in a file:  ~/.wp-release
