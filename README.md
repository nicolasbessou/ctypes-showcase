C-Python binding using ctypes
=============================

Introduction
------------

Here is an example of code that shows how to do a C-Python binding using ctypes and ctypesgen.

- [ctypes](https://docs.python.org/2.7/library/ctypes.html) provides C compatible data types, and allows calling functions in DLLs or shared libraries.
- [ctypesgen](https://github.com/davidjamesca/ctypesgen) automatically generates a wrapper (as  a python module) that matches the C API in header files.

How does it works?
------------------
- Write a C function
- Make it a shared library
- Run ctypesgen to generate the Python binding module from the DLL and the C header
- Call the C function in python using the generated python module.

What is the tricky part?
------------------------
The tricky part is to properly call the C function from the Python script.
The conversion from python types (int, float, arrays, numpy) to ctypes types is not always very intuitive.

This demo shows how to call C functions with:
- several native python types
- numpy arrays
- C structures

NOTE: ctypesgen does not support C++ APIs. So you need a C API for it to work (no class, C++ types or C++ templates). However, you can use C++ code inside your functions.

How to run the demo?
--------------------

First, You need to have python, ctypesgen, numpy and gcc installed on your machine.

Then, compile the C Dll that will be called by Python.
```
python waf configure
python waf build -v
```
The above commands compile the `algo.c` and run ctypesgen using `algo.h` to generate the python binding script `_build/genApiAlgo.py`.


Run the python code that loads the compiled C Dll and call C functions
```
python runDemo.py
```
This script calls the `_build/genApiAlgo.py` which calls the C functions using the compiled DLL.

Look at the python script to show how the C functions are called and how the arguments are provided.
