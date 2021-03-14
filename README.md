<a href="https://www.sparkpost.com"><img src="https://www.sparkpost.com/sites/default/files/attachments/SparkPost_Logo_2-Color_Gray-Orange_RGB.svg" width="200px"/></a>

[Sign up](https://app.sparkpost.com/join?plan=free-0817?src=Social%20Media&sfdcid=70160000000pqBb&pc=GitHubSignUp&utm_source=github&utm_medium=social-media&utm_campaign=github&utm_content=sign-up) for a SparkPost account and visit our [Developer Hub](https://developers.sparkpost.com) for even more content.

# sparkyTemplate
[![Build Status](https://travis-ci.com/tuck1s/sparkyTemplate.svg?branch=main)](https://travis-ci.com/tuck1s/sparkyTemplate)

Command-line tool for working with SparkPost templates, supporting the following options:
- List templates in your account (CSV output) similar to the SparkPost Web UI list / "save as CSV" option

- Retrieve a template by ID. The output defaults to JSON. You can also write the content into separate text, HTML, AMP HTML files which is useful for working on templates offline.

- Update the headers. This option is provided here, and not currently in the SparkPost web UI.

Updating the headers is useful, for example, if you wish to include recipients in "CC".

Not yet included: Create and Delete functions, because the SparkPost web UI already supports these.

## Easy installation

Firstly ensure you have `python3`, `pip` and `git`.

Next, get the project. Install `pipenv` (`--user` option recommended, [see this article](https://stackoverflow.com/questions/42988977/what-is-the-purpose-pip-install-user)) and use this to install the project dependencies.
```
git clone https://github.com/tuck1s/sparkyTemplate.git
cd sparkyTemplate
pip install --user pipenv
pipenv install
pipenv shell
```
_Note: In the above commands, you may need to run `pip3` instead of `pip`._

`./sparkyTemplate.py -h` for usage info.

## Pre-requisites

Set the following environment variables. Note these are case-sensitive.

```
SPARKPOST_HOST (optional)
    The URL of the SparkPost API service you're using. Defaults to https://api.sparkpost.com.

SPARKPOST_API_KEY
    API key on your SparkPost account, with Templates: Read/Write rights.
```

## Usage

```
./sparkyTemplate.py -h
usage: sparkyTemplate.py [-h] {list,retrieve,write_headers} ...

SparkPost template update utility

positional arguments:
  {list,retrieve,write_headers}
                        sub-command help
    list                List all templates in this account
    retrieve            retrieve a template
    write_headers       Write headers to an existing template (overwriting any existing headers)

optional arguments:
  -h, --help            show this help message and exit
```

The sub-commands `list`, `retrieve`, `write_headers` each have their own usage help.

### List
```
./sparkyTemplate.py list -h
usage: sparkyTemplate.py list [-h] [--draft {False,True}] [--shared_with_subaccounts {False,True}]

optional arguments:
  -h, --help            show this help message and exit
  --draft {False,True}  If true, returns the draft templates. If false, returns the published templates. When not provided, returns the most recently edited templates (draft or
                        published).
  --shared_with_subaccounts {False,True}
                        If true, returns only shared templates. If false, returns only non-shared templates.
```

### Retrieve

```
./sparkyTemplate.py retrieve -h
usage: sparkyTemplate.py retrieve [-h] [--draft {False,True}] [--outfile OUTFILE] id

positional arguments:
  id                    Identity of the template

optional arguments:
  -h, --help            show this help message and exit
  --draft {False,True}  If true, returns the draft template. If false, returns the published template. When not provided, returns the most recently edited template (draft or
                        published).

Special options:
  --outfile OUTFILE     Instead of printing JSON (default), store each content part to files OUTFILE.txt, .html, .amp.html
```

### Write headers
This provides a feature that is not currently surfaced in the SparkPost web UI.

```
./sparkyTemplate.py write_headers -h
usage: sparkyTemplate.py write_headers [-h] [--update_published {False,True}] [--headers HEADERS] id

positional arguments:
  id                    Identity of the template

optional arguments:
  -h, --help            show this help message and exit
  --update_published {False,True}
                        An existing published version can be overwritten directly by setting the update_published query parameter to true. If the query param is not passed or
                        set to false, it will result in an update to the draft version.
  --headers HEADERS     JSON-formatted string with headers to add, e.g. {"CC": "{{my_cc}}"}
```

To make your command-line shell pass the HEADERS value literally, enclose in single quotes, e.g.

```
./sparkyTemplate.py write_headers avocado-goodness --headers  '{"cats": "boots", "dogs": "shoes"}'
```

When `--update_published=true`, the tool reads the template *published* content, then writes it back to the *published* content.

When omitted (or set to `false`), the tool will read the template *draft* content and write it back to the *draft* content.

> Tip: you can promote draft content to published content via the SparkPost web UI.

## See Also

1. [Header template object](https://developers.sparkpost.com/api/templates/#header-template-object)

1. [Header notes](https://developers.sparkpost.com/api/templates/#header-header-notes)

1. [Update a published template](https://developers.sparkpost.com/api/templates/#templates-put-update-a-published-template)

1. [SparkPost Developer Hub](https://developers.sparkpost.com/)

