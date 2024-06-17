# mixer.py

[![Nuget](https://img.shields.io/pypi/v/mixer.py?color=%23FF00FF&style=for-the-badge)](https://pypi.org/project/mixer.py/)

An unofficial Mixer API wrapper written in Python.

See my other project [mixcord](https://github.com/ooojustin/mixcord) for an example of implementation.

***Note:** This project was written for the [streaming platform owned by Microsoft](https://en.wikipedia.org/wiki/Mixer_(service)), which shut down in 2020.* 

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

As of the end of 2019 (shortly before the demise of Mixer), this project was still being developed. Several months later in 2020, the platform was shutdown, ending development as a result. The code still serves as a good example of an object-oriented Python API wrapper.
