# OLang 2 - Beta 1.0.0

OLang is a modern, lightweight programming language designed for simplicity and efficiency. It's ideal for scripting, educational use, and rapid prototyping. OLang features a clean syntax, dynamic typing, and a powerful standard library.

## Installation:

To install OLang, download the latest binary (bin folder) from the official repository and run the installation script called **setup.exe**.
Firstly, you will need to accept the license agreement. After that, you will be prompted to choose configuration, default libraries and the installation directory.
After installation, you can run OLang scripts by double-clicking the file with _.olang_ extension, or by using **'olang [filename]'** command with optional params: --debug for forcing preprocessor debugging and --ignore for ignoring fatal errors and running the code anyways. OLang will automatically open the script in the default command prompt application. You will be able to configure your interpreter there or skip the process by applying default settings.

## Configuration:

**File: config.json**

- preprocessorDebug: true / false; if true, preprocessor will print information about libraries, objects and code before running the program
- returnOnFatal: true / false; if true, interpreter will stop code execution if it encounters a fatal error.
- generalLibraryLocation: str; directory name where libraries are stored
- includeLibraries: list[str]; list of libraries which should be included automatically even if they are not included using $use instruction

**You can also configure your OLang during installation process!**

### Read more about the project in the article (Architektura i Implementacja interpretera w Pythonie.pdf)

### Read about the syntax, different libraries and more in the HTML documentation located in source/docs/index.html file in the project's binary.

## To Do List:

- Add else statement
- Add math library with instructions like sqrt(), ceil(), abs(), or floor()
- Add os library with instructions like open(), makefile(), listfiles(), or cmd()
- Fix bugs discovered in the beta release
