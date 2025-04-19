# PythonTemplateRepo

![Made in Python badge](./docs/badges/made-in-python.svg)

![Works on Windows badge](./docs/badges/works-on-windows-cozy.svg)
![Works on Mac badge](./docs/badges/works-on-mac-cozy.svg)
![Works on Linux badge](./docs/badges/works-on-linux-cozy.svg)

[Image credits](./image-credits.md)

This is a basic README template. Feel free to customise it to your liking.

## Features

- Feature 1
- Feature 2

[See the documentation](../docs/) for more.

## Options to run

You can run the program from source or use a pre-compiled binary.

Pre-compiled binaries are available either from the Releases tab (if the developer chooses to add them there) or after each push from the Actions tab (GitHub account required). Please be aware that using binaries from the Actions tab is very dangerous, as it is considered untested software.

To run the program from source, you'll need to have the following prerequisites:

- Python 3.11 <!-- Change this to the version of Python this is being developed in -->
- Git (note that this is not a necessary but it's often best to have such)

- Clone this repository using:

```bash
git clone https://github.com/{username}/{repo}
```

- Then, setup a virtual environment:

```bash
python -m venv venv
venv\scripts\activate
pip install -r requirements.txt
```

- Finally, run the necessary command for your situation:

```bash
# Running the program itself
python main.py
# Viewing the MkDocs site
mkdocs serve
# Freezing the application
pyinstaller --onefile main.py
```

And all done!
