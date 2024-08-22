# Light analyzer

Uses functions from the OpenCV library to detect anomalies in light sources.

The below GIF highlights a simple example:

![GIF of sample one](sample_gifs/sample_gif_one.gif)

The below GIF illustrates a more difficult example, making use of a different threshold algorithm and swapping between image channels.

![GIF of sample two](sample_gifs/sample_gif_two.gif)

## Installation steps:

1. Check that you have the correct python version installed, which can be found inside `.python-version`.
    - if you're unsure how to manage multiple python installations, [pyenv](https://github.com/pyenv/pyenv) is a good solution.
    - If you're running this on a PC, it's good practice to create a [virtualenv](https://virtualenv.pypa.io/en/latest/user_guide.html).
2. Run the following command inside a terminal:
```bash
pip install -r requirements.txt
```


## TODO:
 - [ ] Rewrite to use `.kv` files where applicable :)