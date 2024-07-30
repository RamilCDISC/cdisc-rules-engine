### Supported python versions

[![Python 3.9](https://img.shields.io/badge/python-3.9-green.svg)](https://www.python.org/downloads/release/python-390)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-310)

# cdisc-rules-engine

Open source offering of the cdisc rules engine

### **Quick start**

To quickly get up and running with CORE, users can download the latest executable version of the engine for their operating system from here: <https://github.com/cdisc-org/cdisc-rules-engine/releases>

Once downloaded, simply unzip the file and run the following command based on your Operating System:

Windows:

```
.\core.exe validate -s <standard> -v <standard_version> -d path/to/datasets

# ex: .\core.exe validate -s sdtmig -v 3-4 -d .\xpt\
```

Linux/Mac:

```
./core validate -s <standard> -v <standard_version> -d path/to/datasets

# ex: ./core validate -s sdtmig -v 3-4 -d .\xpt\
```

### **Code formatter**

This project uses the `black` code formatter, `flake8` linter for python and `prettier` for JSON, YAML and MD.
It also uses `pre-commit` to run `black`, `flake8` and `prettier` when you commit.
Both dependencies are added to _requirements.txt_.

**Required**

Setting up `pre-commit` requires one extra step. After installing it you have to run

`pre-commit install`

This installs `pre-commit` in your `.git/hooks` directory.

### **Installing dependencies**

These steps should be run before running any tests or core commands using the non compiled version.

- Create a virtual environment:
  `python -m venv <virtual_environment_name>`
- Activate the virtual environment:

`./<virtual_environment_name>/bin/activate` -- on linux/mac </br>
`.\<virtual_environment_name>\Scripts\Activate` -- on windows

- Install the requirements.

`python -m pip install -r requirements.txt` # From the root directory

### **Running The Tests**

From the root of the project run the following command (this will run both the unit and regression tests):

`python -m pytest tests`

### **Running a validation**

#### From the command line

Clone the repository and run `python core.py --help` to see the full list of commands.

Run `python core.py validate --help` to see the list of validation options.

```
  -ca, --cache TEXT               Relative path to cache files containing pre
                                  loaded metadata and rules
  -ps, --pool-size INTEGER         Number of parallel processes for validation
  -d, --data TEXT                 Path to directory containing data files
  -dp, --dataset-path TEXT        Absolute path to dataset file. Can be specified multiple times.
  -dxp, --define_xml_path TEXT    Path to Define-XML
  -l, --log-level [info|debug|error|critical|disabled|warn]
                                  Sets log level for engine logs, logs are
                                  disabled by default
  -rt, --report-template TEXT     File path of report template to use for
                                  excel output
  -s, --standard TEXT             CDISC standard to validate against
                                  [required]
  -v, --version TEXT              Standard version to validate against
                                  [required]
  -ct, --controlled-terminology-package TEXT
                                  Controlled terminology package to validate
                                  against, can provide more than one
  -o, --output TEXT               Report output file destination
  -of, --output-format [JSON|XLSX]
                                  Output file format
  -rr, --raw-report               Report in a raw format as it is generated by
                                  the engine. This flag must be used only with
                                  --output-format JSON.
  -dv, --define-version TEXT      Define-XML version used for validation
  -dxp, --define-xml-path         Path to define-xml file.
  --whodrug TEXT                  Path to directory with WHODrug dictionary
                                  files
  --meddra TEXT                   Path to directory with MedDRA dictionary
                                  files
  -r, --rules TEXT                Specify rule core ID ex. CORE-000001. Can be specified multiple times.
  -lr, --local_rules TEXT         Specify relative path to directory containing
                                  local rule yml and/or json rule files.
  -lrc, --local_rules_cache       Adding this flag tells engine to use local rules
                                  uploaded to the cache instead of published rules
                                  in the cache for the validation run.
  -lri, --local_rule_id TEXT      Specify ID for custom, local rules in the cache
                                  you wish to run a validation with.
  -vo, --verbose-output           Specify this option to print rules as they
                                  are completed
  -p, --progress [verbose_output|disabled|percents|bar]
                                  Defines how to display the validation
                                  progress. By default a progress bar like
                                  "[████████████████████████████--------]
                                  78%"is printed.
  --help                          Show this message and exit.
```

##### Available log levels

- `debug` - Display all logs
- `info` - Display info, warnings, and error logs
- `warn` - Display warnings and errors
- `error` - Display only error logs
- `critical` - Display critical logs

##### **Validate folder**

To validate a folder using rules for SDTM-IG version 3.4 use the following command:

    `python core.py validate -s sdtmig -v 3-4 -d path/to/datasets`

##### **Understanding the Rules Report**

The rules report tab displays the run status of each rule selected for validation

The possible rule run statuses are:

- `SUCCESS` - The rule ran and data was validated against the rule. May or may not produce results
- `SKIPPED` - The rule was unable to be run. Usually due to missing required data, but could also be cause by rule execution errors.

##### Additional Core Commands

**- update-cache** - update locally stored cache data (Requires an environment variable - `CDISC_LIBRARY_API_KEY`)

    `python core.py update-cache`

To obtain an api key, please follow the instructions found here: <https://wiki.cdisc.org/display/LIBSUPRT/Getting+Started%3A+Access+to+CDISC+Library+API+using+API+Key+Authentication>. Please note it can take up to an hour after sign up to have an api key issued

- an additional local rule `-lr` flag can be added to the update-cache command that points to a directory of local rules. This adds the rules contained in the directory to the cache. It will not update the cache from library when `-lr` is specified. A `-lri` local rules ID must be given when -lr is used to ID your rules in the cache.
  **NOTE:** local rules must contain a 'custom_id' key to be added to the cache. This should replace the Core ID field in the rule.

            `python core.py update-cache -lr 'path/to/directory' -lri 'CUSTOM123'`

- to remove local rules from to the cache, remove rules `-rlr` is added to update-cache to remove local rules from the cache. A previously used local_rules_id can be specified to remove all local rules with that ID from the cache or the keyword 'ALL' is reserved to remove all local rules from the cache.

          `python core.py update-cache -rlr 'CUSTOM123'`

**- list-rules** - list published rules available in the cache

- list all published rules:

      `python core.py list-rules`

- list rules for standard:

      `python core.py list-rules -s sdtmig -v 3-4`

-list all local rules:

      `python core.py list-rules -lr`

-list local rules with a specific local rules id:

      `python core.py list-rules -lr -lri 'CUSTOM1'`

**- list-rule-sets** - lists all standards and versions for which rules are available:
`python core.py list-rule-sets`

**- test** - Test authored rule given dataset in json format

```
  -ca, --cache TEXT               Relative path to cache files containing pre
                                  loaded metadata and rules
  -dp, --dataset-path TEXT        Absolute path to dataset file
  -s, --standard TEXT             CDISC standard to validate against
                                  [required]
  -v, --version TEXT              Standard version to validate against
                                  [required]
  -ct, --controlled-terminology-package TEXT
                                  Controlled terminology package to validate
                                  against, can provide more than one
  -dv, --define-version TEXT      Define-XML version used for validation
  --whodrug TEXT                  Path to directory with WHODrug dictionary
                                  files
  --meddra TEXT                   Path to directory with MedDRA dictionary
                                  files
  -r, --rule TEXT                 Path to rule json file.
  -dxp                            Path to define-xml file.
  --help                          Show this message and exit.
```

EX: `python core.py test -s sdtmig -v 3-4 -dp <path to dataset json file> -r <path to rule json file> --meddra ./meddra/ --whodrug ./whodrug/`
Note: JSON dataset should match the format provided by the rule editor:

```
{
    "datasets": [{
      "filename": "cm.xpt",
      "label": "Concomitant/Concurrent medications",
      "domain": "CM",
      "variables": [
        {
          "name": "STUDYID",
          "label": "Study Identifier",
          "type": "Char",
          "length": 10
        }
      ],
      "records": {
        "STUDYID": [
          "CDISC-TEST",
          "CDISC-TEST",
          "CDISC-TEST",
          "CDISC-TEST"
        ],
      }
    }
  ]
}
```

**- list-ct** - list ct packages available in the cache

```
Usage: python core.py list-ct [OPTIONS]

  Command to list the ct packages available in the cache.

Options:
  -c, --cache_path TEXT  Relative path to cache files containing pre loaded
                         metadata and rules
  -s, --subsets TEXT     CT package subset type. Ex: sdtmct. Multiple values
                         allowed
  --help                 Show this message and exit.
```

#### **PyPI Quickstart: Validate data within python**

An alternative to running the validation from the command line is to instead import the rules engine library in python and run rules against data directly (without needing your data to be in `.xpt` format).

##### Step 0: Install the library

```
pip install cdisc-rules-engine
```

In addition to installing the library, you'll also want to download the rules cache (found in the `resources/cache` folder of this repository) and store them somewhere in your project.

##### Step 1: Load the Rules

The rules can be loaded into an in-memory cache by doing the following:

```python
import os
import pathlib

from multiprocessing.managers import SyncManager
from cdisc_rules_engine.services.cache import InMemoryCacheService

class CacheManager(SyncManager):
    pass

# If you're working from a terminal you may need to
# use SyncManager directly rather than define CacheManager
CacheManager.register("InMemoryCacheService", InMemoryCacheService)


def load_rules_cache(path_to_rules_cache):
  cache_path = pathlib.Path(path_to_rules_cache)
  manager = CacheManager()
  manager.start()
  cache = manager.InMemoryCacheService()

  files = next(os.walk(cache_path), (None, None, []))[2]

  for fname in files:
      with open(cache_path / fname, "rb") as f:
          cache.add_all(pickle.load(f))

  return cache
```

Rules in this cache can be accessed by standard and version using the `get_rules_cache_key` function.

```python
from cdisc_rules_engine.utilities.utils import get_rules_cache_key

cache = load_rules_cache()
# Note that the standard version is separated by a dash, not a period
cache_key_prefix = get_rules_cache_key("sdtmig", "3-4")
rules = cache.get_all_by_prefix(cache_key_prefix)
```

`rules` will now be a list of dictionaries the following keys

- `core_id`
  - e.g. "CORE-000252"
- `domains`
  - e.g. `{'Include': ['DM'], 'Exclude': []}` or `{'Include': ['ALL']}`
- `author`
- `reference`
- `sensitivity`
- `executability`
- `description`
- `authorities`
- `standards`
- `classes`
- `rule_type`
- `conditions`
- `actions`
- `datasets`
- `output_variables`

##### Step 2: Prepare your data

In order to pass your data through the rules engine, it must be a pandas dataframe of an SDTM dataset. For example:

```
>>> data
STUDYID DOMAIN USUBJID  AESEQ AESER    AETERM    ... AESDTH AESLIFE AESHOSP
0          AE      001     0     Y     Headache  ...     N       N       N

[1 rows x 19 columns]
```

Before passing this into the rules engine, we need to wrap it in a DatasetVariable.

```python
from cdisc_rules_engine.models.dataset_variable import DatasetVariable

dataset = DatasetVariable(data)
```

##### Step 3: Run the (relevant) rules

Next, we need to actually run the rules. We can select which rules we want to run based on the domain of the data we're checking and the `"Include"` and `"Exclude"` domains of the rule.

```python
# Get the rules for the domain AE
# (Note: we're ignoring ALL domain rules here)
ae_rules = [
  rule for rule in rules
  if "AE" in rule["domains"].get("Include", [])
]
```

There's one last thing we need before we can actually run the rule, and that's a `COREActions` object. This object will handle generating error messages should the rule fail.

To instantiate a `COREActions` object, we need to pass in the following:

- `results`: An array to which errors will be appended
- `variable`: Our DatasetVariable
- `domain`: e.g. "AE"
- `rule`: Our rule

```python
from cdisc_rules_engine.models.actions import COREActions

rule = ae_rules[0]
results = []
core_actions = COREActions(
  results,
  variable=dataset,
  domain="AE",
  rule=rule
)
```

All that's left is to run the rule!

```python
from business_rules.engine import run

was_triggered = run(
  rule=rule,
  defined_variables=dataset_variable,
  defined_actions=core_actions,
)
```

##### Step 5: Interpret the results

The return value of run will tell us if the rule was triggered.

- A `False` value means that there were no errors
- A `True` value means that there were errors

If there were errors, they will have been appended to the results array passed into your `COREActions` instance. Here's an example error:

```python
{
  'executionStatus': 'success',
  'domain': 'AE',
  'variables': ['AESLIFE'],
  'message': 'AESLIFE is completed, but not equal to "N" or "Y"',
  'errors': [
    {'value': {'AESLIFE': 'Maybe'}, 'row': 1}
  ]
}
```

### **Creating an executable version**

**Linux**

`pyinstaller core.py --add-data=venv/lib/python3.9/site-packages/xmlschema/schemas:xmlschema/schemas --add-data=resources/cache:resources/cache --add-data=resources/templates:resources/templates`

**Windows**

`pyinstaller core.py --add-data=".venv/Lib/site-packages/xmlschema/schemas;xmlschema/schemas" --add-data="resources/cache;resources/cache" --add-data="resources/templates;resources/templates"`

_Note .venv should be replaced with path to python installation or virtual environment_

This will create an executable version in the `dist` folder. The version does not require having Python installed and
can be launched by running `core` script with all necessary CLI arguments.

### **Creating .whl file**

All non-python files should be listed in `MANIFEST.in` to be included in the distribution.
Files must be in python package.

**Unix/MacOS**

`python3 -m pip install --upgrade build`
`python3 -m build`

To install from dist folder
`pip3 install {path_to_file}/cdisc_rules_engine-{version}-py3-none-any.whl`

To upload built distributive to pypi

`python3 -m pip install --upgrade twine`
`python3 -m twine upload --repository {repository_name} dist/*`

**Windows(Untested)**

`py -m pip install --upgrade build`
`py -m build`

To install from dist folder
`pip install {path_to_file}/cdisc_rules_engine-{version}-py3-none-any.whl`

To upload built distributive to pypi

`py -m pip install --upgrade twine`
`py -m twine upload --repository {repository_name} dist/*`
