# PythonTemplateRepo

![Works on Windows badge](../docs/badges/works-on-windows-cozy-minimal.svg)
![Works on Mac badge](../docs/badges/works-on-mac-cozy-minimal.svg)
![Works on Linux badge](../docs/badges/works-on-linux-cozy-minimal.svg)

Template repo for getting started with a Python project.

## Getting started

To get started, click on the `Use this template` at the top-right of the screen, then enter your project's name and any other info you want.

You might see that some GitHub Actions runs will fail. This is normal. After some tweaking to them, they will work as your expect them to be, but you can choose to deal with that once you're all done.

## Directories

### docs/

The `docs` directory is the documentation folder. In Python, we can use `MkDocs` to make easy documentation without having to spend time on making a fancy site. MkDocs uses Markdown (.md) files placed in the `docs` directory to output a site that can be used as your documentation site for your program. It has many themes and plugins that you can choose from; though beware that to install those themes, you will have to install their libraries akin to running the author's code.

For more information, [visit MkDocs' website](https://www.mkdocs.org/).

### tests/

The `tests` directory is the unit tests folder, where all your unit tests will go. In Python, we can use `pytest` to have our code tested before setting it for production. You can ad tests by creating a folder named `test_` and then your script's name, for example, `test_main`. Inside, place a blank `__init__.py` file to let Python know that this is a module, and then you can run `pytest` in your terminal and see if your tests have passed or failed.

For more information on Pytest, [visit Pytest's docs](https://docs.pytest.org/en/stable/).

To learn about test-driven development, [Wikipedia is a good starting point](https://en.wikipedia.org/wiki/Test-driven_development)

### images/

The `images` directory is where you can store images you want to use. You can have app icons, badges, anything that has an image into that folder.

### .vscode/

The `.vscode` folder contains stuff that can only be used in Visual Studio Code (and any forks of its kind). This includes:

- `/extensions.json` - Recommended VSCode extensions to use.
- `launch.json` - Debug launch configs for VSCode.

### .github/

The `.github` folder contains GitHub-related stuff, such as:

- `/workflows` - GitHub Actions workflow files that tells GitHub's runners how to behave on certain events.
- `/dependabot.yml` - Dependabot's configuration file, which tells it what to update and how/where. [Learn more about Dependabot](https://docs.github.com/en/code-security/dependabot/working-with-dependabot).
- `/README.md` - not actually something specific to GitHub, but it's an actual README file that you're welcome to take and adapt for your own project, to use over this README file. Remember to delete this after you fork the repo and start making changes!
