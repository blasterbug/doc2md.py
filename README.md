# doc2md.py

pydocmd generates Python documentation in the Markdown (md) format. It was
written to automatically generate documentation that can be put on Github or Bitbucket wiki pages. It is initially based on Ferry Boender's [pydocmd].

It is as of yet not very complete and is more of a Proof-of-concept than a
fully-fledged tool. Markdown is also a very restricted format and every
implementation works subtly, or completely, different. This means output
may be different on different converters.

* __Author__: blasterbug
* __Version__: 0.2b
* __License__: MIT (expat) License

## Usage

    $ python pydocmd.py module [...]

pydocmd scan every python files (.py) given and generate the documentation in
a subfolder `doc`

## Example output

 - [blasterbug/SmileANN/wiki/neuron](http://github.com/blasterbug/SmileANN/wiki/neuron)
 - [blasterbug/SmileANN/wiki/faces](http://github.com/blasterbug/SmileANN/wiki/faces)
 - [blasterbug/pydocmd/wiki/pydocmd](http://github.com/blasterbug/pydocmd/wiki/pydocmd)


[pydocmd]: https://github.com/fboender/pydocmd
