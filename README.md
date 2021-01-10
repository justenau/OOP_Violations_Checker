# Automated detection of object oriented programming principles violation

Tool aiming to automatically detect OOP principle violations in Python code. Currently only Single Responsbility and Liskov Substitution principle checkers are implemented.

## Usage
* Make sure `OOP_Violations_Checker` directory is added to `PYTHONPATH`. 
* Add `.pylintrc` to the root directory of the project you want to analyze. This file contains the whole Pylint configuration. The default configuration disables all Pylint checkers except for custom SRP and LSP checkers. Also `max-ccm` option is related to SRP checker and could be changed if neccessary.
* Run `pylint <directory>` with the name of the directory you want to analyze or `pylint <modules>` providing file names if you want to analyze only certain files.
* It's also possible to configure Pylint to run in your IDE, check Pylint documentation for more info.

## Technical decisions
### SRPChecker
`SRPChecher` evaluates classes based on LCOM (Lack of Cohesion of Methods) and CCM (Cyclomatic Complexity per Method) metrics. It raises warnings if LCOM > 1 or if CCM > 10 (this can be changed by editing `max-ccm` in config).


To calculate LCOM for each classes, additional library (`lcom`) is used. 


For CCM calculation, logic from `mccabe` tool is reused.

### LSPChecker
`LSPChecker` looks for overriden methods in derived classes and raises warnings if after overriding the function it raises `NotImplementedError` or calls `pass` (aka degenerates the base method).