#!/usr/bin/env python3
import sys, argparse, requests, csv, json
from urllib.parse import urljoin
from common import eprint, getenv_check, getenv, host_cleanup, strip_start,\
    add_str_args, add_boolean_args, add_json_args

T = 20                  # Global timeout value for API requests

def list_templates(url, api_key, args):
    """
    List all SparkPost templates with specified endpoint URL, API Key, and query args.
    """
    qp = query_obj(vars(args), [])
    response = api_get(url, api_key, qp)
    if response.status_code == 200:
        templates = response.json().get('results')
        if templates:
            fieldnames = ['id', 'name', 'published', 'description', 'has_draft', 'has_published',
                'last_use', 'last_update_time','shared_with_subaccounts']
            fh = csv.DictWriter(sys.stdout, fieldnames=fieldnames, restval='', extrasaction='ignore')
            fh.writeheader()
            fh.writerows(templates)
    else:
        eprint(response.status_code, response.text)


def retrieve_template(url, api_key, args):
    """
    Get SparkPost template with specified endpoint URL, API Key, and search params.
    """
    qp = query_obj(vars(args), ['id, file'])
    # id is passed in path, not query params
    response = api_get(urljoin(url, args.id), api_key, qp)
    if response.status_code == 200:
        template = response.json().get('results')
        if template:
            if args.outfile:
                # Write content into separate files
                content = template.get('content')
                parts = ['text', 'html', 'amp_html']
                file_extensions = ['.txt', '.html', '.amp.html']
                for k, v in content.items():
                    if k in parts:
                        # Store the content in files
                        idx = parts.index(k)
                        fname = args.outfile + file_extensions[idx]
                        stderr_report('Writing {} file'.format(k), fname)
                        with open(fname, 'w') as fh:
                            fh.write(v)
                    else:
                        stderr_report(k, v) # comfort-reporting
            else:
                # Print as JSON
                print(json.dumps(template))
    else:
        eprint(response.status_code, response.text)


def write_headers_to_template(url, api_key, args):
    """
    Write headers to SparkPost template with specified endpoint URL, API Key, and search params.
    If update_published is true, we always fetch the *published* version and work on that
    """
    if args.update_published == True:
        qp = {'draft' : False} # fetch published version
    else:
        qp = {'draft' : True} # fetch draft version
    # id is passed in path
    response = api_get(urljoin(url, args.id), api_key, qp)
    if response.status_code == 200:
        template = response.json().get('results')
        if template:
            version = 'Published' if template.get('published') else 'Draft'
            stderr_report('Working on', version)
            stderr_report('Previous headers', template['content'].get('headers'))
            if args.headers:
                template['content']['headers'] = args.headers
                put_response = api_put(urljoin(url, args.id), api_key, qp, template)
                if put_response.status_code == 200:
                    stderr_report('Updated headers', template['content'].get('headers'))
                else:
                    eprint(put_response.status_code, put_response.text)
            else:
                eprint('No new headers specified - template not changed')
    else:
        eprint(response.status_code, response.text)


def api_get(url, api_key, query_params):
    headers = {'Authorization': api_key, 'Accept': 'application/json', 'Content-Type': 'application/json'}
    try:
        response = requests.get(url, timeout=T, headers=headers, params=query_params)
        return response
    except ConnectionError as err:
        eprint('error code', err.status_code)
        return None


def api_put(url, api_key, query_params, data):
    headers = {'Authorization': api_key, 'Accept': 'application/json', 'Content-Type': 'application/json'}
    try:
        response = requests.put(url, timeout=T, headers=headers, params=query_params, json=data)
        return response
    except ConnectionError as err:
        eprint('error code', err.status_code)
        return None


def query_obj(arg_dict, non_api_opts):
    """
    Build a SparkPost API object from args (passed in as a dict). Skip callable (function) args
    """
    opt_prefix = 'options.'
    query_obj = { 'options': {}  }
    for key, val in arg_dict.items(): # iterate through args as a dict
        if callable(val) or key in non_api_opts or val == None: # these are not needed in the API call
            continue
        elif key.startswith(opt_prefix):
            stderr_report(key, val)
            query_obj['options'][strip_start(key, opt_prefix)] = val
        else:
            stderr_report(key, val)
            query_obj[key] = val
    return query_obj


def stderr_report(key, val, **kwargs):
    """
    Reporting via stderr, with fixed key : value tabulation
    """
    vstr = json.dumps(val) if isinstance(val, dict) else val
    eprint('{:24} {}'.format(key + ':', vstr), **kwargs)


# -----------------------------------------------------------------------------------------
# Main code
# -----------------------------------------------------------------------------------------
p = argparse.ArgumentParser(description='SparkPost template update utility')
sub_p = p.add_subparsers(help='Sub-command help')

p_list = sub_p.add_parser('list', help='List all templates in this account')
add_boolean_args(p_list, [
    ('draft', 'If true, returns the draft templates. If false, returns the published templates. \
        When not provided, returns the most recently edited templates (draft or published).'),
    ('shared_with_subaccounts', 'If true, returns only shared templates. If false, \
        returns only non-shared templates.')
])
p_list.set_defaults(func=list_templates)

p_retrieve = sub_p.add_parser('retrieve', help='retrieve a template')
p_retrieve.add_argument('id', type=str, help='Identity of the template')
add_boolean_args(p_retrieve, [
    ('draft', 'If true, returns the draft template. If false, returns the published template. \
        When not provided, returns the most recently edited template (draft or published).')
])
pr2 = p_retrieve.add_argument_group('Special options')
pr2.add_argument('--outfile', type=str, help='Instead of printing JSON (default), store each content part to files OUTFILE.txt, .html, .amp.html')
p_retrieve.set_defaults(func=retrieve_template)

p_write_headers = sub_p.add_parser('write_headers', help='Write headers to an existing template (overwriting any existing headers)')
p_write_headers.add_argument('id', type=str, help='Identity of the template')
add_boolean_args(p_write_headers, [
    ('update_published', 'An existing published version can be overwritten directly by setting the update_published query parameter to true. \
        If the query param is not passed or set to false, it will result in an update to the draft version.')
])
add_json_args(p_write_headers, [
    ('headers', r'JSON-formatted string with headers to add, e.g. {"CC": "{{my_cc}}"}')
])
p_write_headers.set_defaults(func=write_headers_to_template)
args = p.parse_args()

api_key = getenv_check('SPARKPOST_API_KEY')                      # API key is mandatory
host = host_cleanup(getenv('SPARKPOST_HOST', default='api.sparkpost.com'))
url = host + '/api/v1/templates/'

if 'func' in vars(args):
    args.func(url, api_key, args)
else:
    p.print_help()