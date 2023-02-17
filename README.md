# perceiver

Segmentation-based tracking algorithms and related.

## Install

Install the following repositories from the source:

- [improcessor](https://github.com/ivapylibs/improcessor)
- [detector](https://github.com/ivapylibs/detector.git)
- [trackpointer](https://github.com/ivapylibs/trackpointer)
- [Lie](https://github.com/ivapylibs/Lie)

```
git clone git@github.com:ivapylibs/perceiver.git
pip3 install -e perceiver[testing]
```

The test files are shell command line executable and should work when
invoked, presuming that pip installation has been performed. If no
modifications to the source code will be performed then the `-e` flag
is not necessary (e.g., use the flag if the underlying code will be
modified).
