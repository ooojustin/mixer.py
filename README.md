# mixer.py

[![Nuget](https://img.shields.io/pypi/v/mixer.py?color=%23FF00FF&style=for-the-badge)](https://pypi.org/project/mixer.py/)

An unofficial Mixer API wrapper written in Python.

See my other project [mixcord](https://github.com/ooojustin/mixcord) for an example of implementation.

## Release Notes

### v0.0.3

__Refactoring__
* Un-verbosified ChatCommands method naming.

__Additions__
* "command" function decorator is now callable.
* Added kwargs support to "command" decorator.
* Added built-in command permissions/role checking via "roles" kwarg.
* Added command name aliasing via "aliases" kwarg.

### v0.0.2

* First release on PyPi. Documentation coming soon.

## Disclaimer

As of August 2019, this project is still heavily under development.

Although it's already on PyPi, breaking changes will likely occur frequently until the release of 1.0.0.
