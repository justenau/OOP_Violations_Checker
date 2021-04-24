# Automated detection of object oriented programming principles violation

Tool aiming to automatically detect OOP principle violations in Python code. Currently only Single Responsbility, Liskov Substitution, Interface Segregation and Dependency Inversion principle checkers are implemented.

## Usage
* Make sure `OOP_Violations_Checker` directory is added to `PYTHONPATH`. 
* Add `.pylintrc` to the root directory of the project you want to analyze. This file contains the whole Pylint configuration. The default configuration disables all Pylint checkers except for custom SRP and LSP checkers. Also `srp-max-ccm`, `srp-max-public-methods` and `srp-max-attributes` options are related to SRP checker and could be changed if neccessary.
* Run `pylint <directory>` with the name of the directory you want to analyze or `pylint <modules>` providing file names if you want to analyze only certain files.
* It is also possible to configure Pylint to run in your IDE, check Pylint documentation for more info.

## Technical decisions
### SRPChecker
`SRPChecher` evaluates classes based on LCOM (Lack of Cohesion of Methods), CCM (Cyclomatic Complexity per Method), maximum public methods per class and maximum attributes per class metrics. It raises warnings if LCOM > 1 or CCM > 10 or amount of methods is class is more than 20 or if amount of attributes in class is more than 15 (last three metrics can be changed by editing config).


To calculate LCOM for each classes, additional library (`lcom`) is used. 


For CCM calculation, logic from `mccabe` tool is reused.


`SRPChecher` is enabled with `srp-compliance` flag.


### LSPChecker
`LSPChecker` looks for overriden methods in derived classes and raises warnings if after overriding the function it raises `NotImplementedError` or calls `pass` (aka degenerates the base method). If both base and derived methods were not implemented, the warning is not raised.


`LSPChecher` is enabled with `lsp-compliance` flag.


### ISPChecker
`ISPChecker` treats all classes which contain only abstract/not implemented methods as interfaces and raises warning if any of client classes (which extend these 'interfaces') does not override all of its methods. In that case, warning is raised.


`ISPChecher` is enabled with `isp-compliance` flag.


### DIPChecker
`DIPChecker` addresses one of the DIP rules stating that `No method should override an implemented base class method`. All child and base class methods with the same naming are compared and if there's any method which was implemented in the base class and then overriden in the child class, warning is raised.


`DIPChecher` is enabled with `dip-compliance` flag.
