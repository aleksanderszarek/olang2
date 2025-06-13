# OLang 2

## Project Work In Progress!

### - Instructions to add: exec(), if, return and for loop.

### - Documentation to add: library documentation

### - Other additions: installation files, arguments for `run.py`

## Current installation method:

1. Install Python with PATH
2. Restart your computer
3. Create `test.olang` file in the same directory as the `run.py` file.
4. Open the file in a text editor and add OLang code.
5. Run `run.py` file by double-clicking it.
   (Default `test.olang` file contains a simple program to check if a string has a substring in it)

## Configuration:

**File: config.json**

- preprocessorDebug: true / false; if true, preprocessor will print information about libraries, objects and code before running the program
- returnOnFatal: true / false; if true, interpreter will stop code execution if it encounters a fatal error.
- generalLibraryLocation: str; directory name where libraries are stored
- includeLibraries: list[str]; list of libraries which should be included automatically even if they are not included using $use instruction

## Read more about the project in the article (Architektura i Implementacja interpretera w Pythonie.pdf)
