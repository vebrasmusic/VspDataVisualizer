# TRAQ Sensors QA

* specifically for TRAQ internal use in generating useful curves from the VSP-3000 and other calibrations, but in general can be a good fresher on GUI stuff for python + analysis.

*** EDIT NOW GOOD FOR QA ***

* uses PyQT, Numpy, Matplotlib 

## How to run


after cloning, cd into the folder and run the following cmd:

``` bash
python -m venv venv
```

then (for Mac):

```bash
source venv/bin/activate
pip install -r requirements.txt
```

or for Windows:
```bash
venv\Scripts\activate
pip install -r requirements.txt
```

btw for windows, you may get a script execution error (some warning), in which case run this first:
```bash
Set-ExecutionPolicy Unrestricted -Scope Process
```

Then, you can use either the automated run by double clicking "run.bat" (ONYL ON WINDOWS)

or manually:

``` bash
python main.py
```


