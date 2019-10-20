# Development

## Initial setup:

```bash
pipenv --three
pipenv install
pipenv install --dev -e .
```

## Running in dev mode

With the above setup you should be able to run commands like:

```bash
csmake --help
```

## Guidelines

### Adding dependencies

Please take care that the license of dependencies use permissive licenses are
compatible with the Apache License 2.0 that the project currently uses. This
can be checked by referring to [ASF Legal Resolved].


### Codestyle

The codestyle for the project is based on [PEP8]. To avoid arguments, code
should be formatted using [Black]


[ASF Legal Resolved]: https://apache.org/legal/resolved.html
[PEP8]: https://www.python.org/dev/peps/pep-0008/
[Black]: https://black.readthedocs.io/en/stable/index.html
