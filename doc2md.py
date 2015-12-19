#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
doc2md.py generates Python documentation in the Markdown (md) format. It was
written to automatically generate documentation that can be put on Github
or Bitbucket wiki pages. It is initially based on Ferry Boender's pydocmd.

It is as of yet not very complete and is more of a Proof-of-concept than a
fully-fledged tool. Markdown is also a very restricted format and every
implementation works subtly, or completely, different. This means output
may be different on different converters.

## Usage

    $ python doc2md.py module [...]

doc2md.py scans every python file (.py) given and generates the documentation
in a subfolder `doc`.

## Example output

 - http://github.com/blasterbug/doc2md.py/wiki/doc2md
 - http://github.com/blasterbug/SmileANN/wiki/neuron
 - http://github.com/blasterbug/SmileANN/wiki/faces

"""



import sys
import os
import imp
import inspect


__author__ = "Benjamin Sientzoff"
__version__ = "0.1.2b"
__maintainer__ = "Benjamin Sientzoff (blasterbug)"
__license__ = "GNU GPL V2"

def remove_extension( fl ):
    """
    Remove extention from the program file name
    """
    # does not handle mutiple dots
    return str(fl).split('.')[0]

def fmt_doc(doc, indent=''):
    """
    Format a doc-string.
    """
    s = ''
    for line in doc.lstrip().splitlines():
        s += '%s%s  \n' % (indent, line.strip())
    return s.rstrip()

def insp_file(file_name):
    """
    Inspect a file and return module information
    """
    mod_inst = imp.load_source(remove_extension( file_name ), file_name)

    if not mod_inst:
        sys.stderr.write("Failed to import '%s'\n" % (file_name))
        sys.exit(2)

    mod_name = inspect.getmodulename(file_name)
    if not mod_name:
        mod_name = os.path.splitext(os.path.basename(file_name))[0]
    return insp_mod(mod_name, mod_inst)

def insp_mod(mod_name, mod_inst):
    """
    Inspect a module return doc, vars, functions and classes.
    """
    info = {
        'name': mod_name,
        'inst': mod_inst,
        'author': {},
        'doc': '',
        'vars': [],
        'functions': [],
        'classes': [],
    }

    # Get module documentation
    mod_doc = inspect.getdoc(mod_inst)
    if mod_doc:
        info['doc'] = mod_doc

    for attr_name in ['author', 'copyright', 'license', 'version', 'maintainer', 'email']:
        if hasattr(mod_inst, '__%s__' % (attr_name)):
            info['author'][attr_name] = getattr(mod_inst, '__%s__' % (attr_name))

    # Get module global vars
    for member_name, member_inst in inspect.getmembers(mod_inst):
        if not member_name.startswith('_') and \
           not inspect.isfunction(member_inst) and \
           not inspect.isclass(member_inst) and \
           not inspect.ismodule(member_inst) and \
           member_inst.__module__ == mod_name and \
           member_name not in mod_inst.__builtins__:
            info['vars'].append( (member_name, member_inst) )

    # Get module functions
    functions = inspect.getmembers(mod_inst, inspect.isfunction)
    if functions:
        for func_name, func_inst in functions:
            if func_inst.__module__ == mod_name :
                info['functions'].append(insp_method(func_name, func_inst))

    # Get module classes
    classes = inspect.getmembers(mod_inst, inspect.isclass)
    if classes:
        for class_name, class_inst in classes:
            if class_inst.__module__ == mod_name :
                info['classes'].append(insp_class(class_name, class_inst))

    return info

def insp_class(class_name, class_inst):
    """
    Inspect class and return doc, methods.
    """
    info = {
        'name': class_name,
        'inst': class_inst,
        'doc': '',
        'methods': [],
    }

    # Get class documentation
    class_doc = inspect.getdoc(class_inst)
#    if class_doc:
        #info['doc'] = fmt_doc(class_doc)

    # Get class methods
    methods = inspect.getmembers(class_inst, inspect.ismethod)
    for method_name, method_inst in methods:
        info['methods'].append(insp_method(method_name, method_inst))

    return info

def insp_method(method_name, method_inst):
    """
    Inspect a method and return arguments, doc.
    """
    info = {
        'name': method_name,
        'inst': method_inst,
        'args': [],
        'doc': ''
    }

    # Get method arguments
    method_args = inspect.getargspec(method_inst)
    for arg in method_args.args:
        if arg != 'self':
            info['args'].append(arg)

    # Apply default argumument values to arguments
    if method_args.defaults:
        a_pos = len(info['args']) - len(method_args.defaults)
        for pos, default in enumerate(method_args.defaults):
            info['args'][a_pos + pos] = '%s=%s' % (info['args'][a_pos + pos], default)

    # Print method documentation
    method_doc = inspect.getdoc(method_inst)
    if method_doc:
        info['doc'] = fmt_doc(method_doc)
    return info


def to_markdown( text_block ) :
    """
    Markdownify an inspect file
    :param text_block: inspect file to turn to Markdown
    :return: Markdown doc into a string
    """
    doc_output = ("# %s  \n" % file_i['name'] )
    doc_output += file_i['doc'] + '  \n'
    author = ''
    if 'author' in file_i['author']:
        author += file_i['author']['author'] + ' '
    if 'email' in file_i['author']:
        author += '<%s>' % (file_i['author']['email'])
    if author:
        doc_output += str("\n __Author__: %s  \n" % author )

    author_attrs = [
        ('Version', 'version'),
        ('Copyright', 'copyright'),
        ('License', 'license'),
    ]
    for attr_friendly, attr_name in author_attrs:
        if attr_name in file_i['author']:
            doc_output += " __%s__: %s  \n" % (attr_friendly, file_i['author'][attr_name])

    if file_i['vars']:
        doc_output += "\n## Variables\n"
        for var_name, var_inst in file_i['vars']:
            doc_output += " - `%s`: %s\n" % (var_name, var_inst)

    if file_i['functions']:
        doc_output += "\n\n## Functions\n"
        for function_i in file_i['functions']:
            if function_i['name'].startswith('_'):
                continue
            doc_output += "\n\n### `%s(%s)`\n" % (function_i['name'], ', '.join(function_i['args']))
            if function_i['doc']:
                doc_output += "%s" % (function_i['doc'])
            else:
                doc_output += "No documentation for this function  "

    if  file_i['classes']:
        doc_output += "\n\n## Classes\n"
        for class_i in file_i['classes']:
            doc_output += "\n\n### class `%s()`\n" % (class_i['name'])
            if class_i['doc']:
                doc_output += "%s  " % (class_i['doc'])
            else:
                doc_output += "No documentation for this class  "

            doc_output += "\n\n### Methods:\n"
            for method_i in class_i['methods']:
                if method_i['name'] != '__init__' and method_i['name'].startswith('_'):
                    continue
                doc_output += "\n\n#### def `%s(%s)`\n" % (method_i['name'], ', '.join(method_i['args']))
                doc_output += "%s  " % (method_i['doc'])
    return doc_output


if __name__ == '__main__':
    if 1 < len(sys.argv) :
        doc_dir = "doc"
        for arg in sys.argv[1:] :
            file_i = insp_file(arg)
            doc_content = to_markdown(file_i)
            if not os.path.exists( doc_dir ) :
                os.makedirs( doc_dir )
            doc_file = open( doc_dir + "/" + remove_extension(arg) + ".md", 'w')
            sys.stdout.write( "Writing documentation for %s in doc/\n" % arg )
            doc_file.write( doc_content )
            doc_file.close()
    else:
        sys.stderr.write('Usage: %s <file.py>\n' % (sys.argv[0]))
        sys.exit(1)
