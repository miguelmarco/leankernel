# Jupyter kernel for Lean


A kernel to use Lean from a Jupyter notebook.

It works by keeping internally a virtual file, formed by the contents of the
evaluated cells, and passing it to the lean server.

Each time a cell is evaluated, the answer from the lean server is parsed. If
there are no errors, the content is added to the virtual file.

## Warning

This is in a proof of concept stage. Please test it, but beware that
some bugs are expected to show.

## Installation

First clone the git repo and pip install it from the corresponding directory:

```
git clone https://github.com/miguelmarco/leankernel.git
cd leankernel
pip install .
```

Then edit the `lean/kernel.json` file and adapt the environment variables to your
lean installation:

- `LEAN_MEMORY` : the amount of RAM to be used by your lean process
- `LEAN_TIME`: the timeout for the lean server
- `LEAN_BINARY` : the lean executable
- `LEAN_PATHFILES` : the path to your `leanpkg.path` file for your lean project (so lean knows where to look for mathlib, for example).

Finally install the kernel by running

```
jupyter kernelspec install leankernel/lean --user
```

This will create a `lean` folder in your jupyter kernels directory (usually `~/.local/share/jupyter/kernels`) and copy the `kernel.json` and logo file there.


## Notes

- If your cell contains the words `hint`, `suggest` or `library_search`, it will
be evaluated only as a temporary content, so you can see the output with the
corresponding suggestions (you need to start importing the `tactic` module for
those tactics to work).

- If your input is only a line with the content
```
-- save filename
```
 the content of the virtual file will be saved to `filename`.

 - If your input is only a line with the content
 ```
-- print
 ```
 it will print the already defined objects and already proven theorems and lemmas

