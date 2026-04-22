# README #

### What is this repository for? ###
This repository is for storing all transactions, accounts, expenses, loans and liabilities. Generate reports around balances, upcoming dues, asset allocation, goal tracking, and portfolio performance compared to benchmarks for various time-periods

### How do I get set up? ###

* **Clone submodules**: git submodule update --init
* **Install ledger-cli**: Double-entry plain text accounting tool
* **Export LEDGER_CONFIG_PREFIX**: This is used for environment level config handling
`export LEDGER_CONFIG_PREFIX='mac.'`
* **Install emacs**: Editor for ledger
* **Setup emacs ledger-mode**: This provides shortcuts and ledger support
* **Install beancount**: Another plain text accounting tool which is more strict than ledger
* **Install fava**: It is the web UI for beancount files
* **Install entr**: This tool watches for file changes and performs some action when that happens. Used for auto conversion of ledger files to beancount when server is running
* **Install cpan module**: This is for fava. command `cpanm DateTime::Format::Strptime` && `cpan File:BaseDir` && `cpan Regexp::Common` && `cpan String::Interpolate` && `cpan YAML::XS` && `cpan enum`
* **Install locales**(only for termux-ubuntu): apt-get install locales; locale-gen en_US.UTF-8
* Update correct `LEDGER_ROOT` path on `scripts/ledger-aliases.sh`
* add the following entry `source <LEDGER_ROOT>/scripts/ledger-aliases.sh` into your `~/.bashrc` or `~/.zshrc`
* add a symlink to ledger account autocomplete plugin `ln -s ~/ledger/scripts/plugins/ledger_account_autocomplete.py ~/.config/sublime-text-3/Packages/User/ledger_autocomplete.py`

### Starting new ledger for Fiscal year ###
* Reads `main.ledger` file and generates equity files using the script below
* Generate closing equity for the year with all directories and files, updates all scripts so that existing system works as is.
* Run
		```ledger-equity.sh <FISCAL_YEAR>```

### Useful ledger commands ###
* Get all of my assets. Everything I own.
		```ledger -f entries/main.ledger --real -V --depth 3 bal Assets```
* Get all of my liabilities, money I have to pay and the money I have to get. If the list that comes after running the command has a positive amount then it is the money I am supposed to get and if the amount is negative then it is the money that I am supposed to pay
		```ledger -f entries/main.ledger --real --depth 3 bal liabilities```
* Get how much I have already invested in my house1
		```cg-valuation```
* Get a view of my current budget across accounts
		```budget```


