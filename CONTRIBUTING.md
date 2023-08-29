## Branching
~~This project uses [GitFlow](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow)
branching model. This will be changed to trunk-based workflow in the future.~~

This project uses [Trunk-based development](https://www.atlassian.com/continuous-delivery/continuous-integration/trunk-based-development).
In this light, every branch must contain a prefix based up on its purpose.
Prefixes are:
- feat
- hotfix
- release

Other prefixes could be introduced in the future.

## Branch Names
Until there is some ticket tracking system implemented for this project, name
branches based on their purpose. For example if you want to add `S3Exporter`
class, branch name should be named `feat/s3-exporter`. Use your best reasoning.

## Code
### Environment
- [Poetry](https://python-poetry.org/) is used for dependency management and
packaging. Execute `poetry install` in project directory to gather
dependencies.
- Use the latest version of Python when ever is possible.
- Set [pre-commit](https://pre-commit.com/).
### General code guidance
- Use proper english words for variables. Name of the variable should reflect
what is inside.
- Follow existing pattern.
- Write reST style type of docstrings. It will be used by a pipeline for
automated documentation builds.
- Your code should be a comment for itself. If there is something that needs
explaining, in a comment, leave a link to a site where this issue is explained.
- This code aims to be a micro framework, less code is usually better. Use
existing libraries and frameworks to achieve a goal, and use Illuminate code
just to glue the whole process.
- Illuminate is async, single threaded framework. It is meant to do I/O from
various sources to various destinations. This defines the scope of the project.
- Code must be covered with tests. 5% drop in coverage will cause build to
fail.
- Code must be covered with documentation.
- Code must be covered with typing hints.
### Security, style, tests and typing
- Formatting is done by [black](https://black.readthedocs.io/en/stable/) with
pre-commit hook.
- [PEP 8](https://peps.python.org/pep-0008/) is the king. It is enforced by
[flake8](https://flake8.pycqa.org/en/latest/) with pre-commit hook.
- Code must pass [bandit](https://bandit.readthedocs.io/en/latest/) check,
triggered by pre-commit hook. Use `# nosec` flag responsibly.
- [MyPy](http://mypy-lang.org/) check is triggered by pre-commit hook.
Currently, typing is the weakest part of this project, since it doesn't have
stubs, and some type hints are wrong, or could be described better with
different types.
- In order to check everything, execute `poetry run tox`.
## Pull Request
- The name of the pull request is the name of the feat branch.
- Check if you have fulfilled requirements to create a PR.
- Always squash feat/hotfix branches before merge.
- PR commit message summary is the name of the feat/hotfix branch and number of
PR given by GitHub. Rest of the message is a list of all commit message on a
feat/hotfix branch, without blank rows in between.
- The only way to merge to master or develop branch is through PR and code
owner approval. All tests must pass.
