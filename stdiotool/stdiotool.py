#!/usr/bin/env python3
# -*- coding: utf8 -*-
# tab-width:4

# pylint: disable=useless-suppression             # [I0021]
# pylint: disable=missing-docstring               # [C0111] docstrings are always outdated and wrong
# pylint: disable=missing-param-doc               # [W9015]
# pylint: disable=missing-module-docstring        # [C0114]
# pylint: disable=fixme                           # [W0511] todo encouraged
# pylint: disable=line-too-long                   # [C0301]
# pylint: disable=too-many-instance-attributes    # [R0902]
# pylint: disable=too-many-lines                  # [C0302] too many lines in module
# pylint: disable=invalid-name                    # [C0103] single letter var names, name too descriptive
# pylint: disable=too-many-return-statements      # [R0911]
# pylint: disable=too-many-branches               # [R0912]
# pylint: disable=too-many-statements             # [R0915]
# pylint: disable=too-many-arguments              # [R0913]
# pylint: disable=too-many-nested-blocks          # [R1702]
# pylint: disable=too-many-locals                 # [R0914]
# pylint: disable=too-few-public-methods          # [R0903]
# pylint: disable=no-member                       # [E1101] no member for base
# pylint: disable=attribute-defined-outside-init  # [W0201]
# pylint: disable=too-many-boolean-expressions    # [R0916] in if statement

from __future__ import annotations

import logging
import os
import sys
import time
from collections.abc import Sequence
from contextlib import contextmanager
from pathlib import Path
from signal import SIG_DFL
from signal import SIGPIPE
from signal import signal

import click
import sh
from asserttool import ic
from click_auto_help import AHGroup
from clicktool import click_add_options
from clicktool import click_global_options
from clicktool import tv
from mptool import mpd_enumerate
from mptool import output
from unmp import unmp

# this should be earlier in the imports, but isort stops working
signal(SIGPIPE, SIG_DFL)


# https://github.com/pyvisa/pyvisa-py/issues/282
@contextmanager
def supress_stderr():
    original_stderr = os.dup(
        2
    )  # stderr stream is linked to file descriptor 2, save a copy of the real stderr so later we can restore it
    blackhole = os.open(
        os.devnull, os.O_WRONLY
    )  # anything written to /dev/null will be discarded
    os.dup2(
        blackhole, 2
    )  # duplicate the blackhole to file descriptor 2, which the C library uses as stderr
    os.close(
        blackhole
    )  # blackhole was duplicated from the line above, so we don't need this anymore
    yield
    os.dup2(original_stderr, 2)  # restoring the original stderr
    os.close(original_stderr)


# https://github.com/pyvisa/pyvisa-py/issues/282
@contextmanager
def supress_stdout():
    original_stdout = os.dup(
        1
    )  # stdout stream is linked to file descriptor 1, save a copy of the real stdout so later we can restore it
    blackhole = os.open(
        os.devnull, os.O_WRONLY
    )  # anything written to /dev/null will be discarded
    os.dup2(
        blackhole, 1
    )  # duplicate the blackhole to file descriptor 2, which the C library uses as stdout
    os.close(
        blackhole
    )  # blackhole was duplicated from the line above, so we don't need this anymore
    yield
    os.dup2(original_stdout, 1)  # restoring the original stdout
    os.close(original_stdout)


@click.group(no_args_is_help=True, cls=AHGroup)
@click_add_options(click_global_options)
@click.pass_context
def cli(
    ctx,
    verbose: bool | int | float,
    verbose_inf: bool,
    dict_output: bool,
) -> None:

    tty, verbose = tv(
        ctx=ctx,
        verbose=verbose,
        verbose_inf=verbose_inf,
    )


## update setup.py if changing function name
## @click.argument("slice_syntax", type=validate_slice, nargs=1)
# @click.command()
# @click.argument("keys", type=str, nargs=-1)
# @click.argument(
#    "sysskel",
#    type=click.Path(
#        exists=False,
#        dir_okay=True,
#        file_okay=False,
#        allow_dash=False,
#        path_type=Path,
#    ),
#    nargs=1,
#    required=True,
# )
# @click.option("--ipython", is_flag=True)
# @click_add_options(click_global_options)
# @click.pass_context
# def cli(
#    ctx,
#    keys: Sequence[str],
#    sysskel: Path,
#    ipython: bool,
#    verbose: bool | int | float,
#    verbose_inf: bool,
#    dict_output: bool,
# ) -> None:
#
#    tty, verbose = tv(
#        ctx=ctx,
#        verbose=verbose,
#        verbose_inf=verbose_inf,
#    )
#
#    iterator: Sequence[dict | bytes] = unmp(
#        valid_types=[
#            dict,
#            bytes,
#        ],
#        verbose=verbose,
#    )
#
#    # need to send a single key, or multiple keys, if multiple keys, keys need to specified on the commandline
#    # either way, the output is still a dict
#
#    index = 0
#    _k = None
#    for index, _mpobject, key_count in mpd_enumerate(iterator, verbose=verbose):
#        # if index == 0:
#        #    first_type = type(_mpobject)
#        #    if first_type == dict:
#        #        key_count = len(list(_mpobject.keys()))
#        #    else:
#        #        key_count = None
#        if key_count > 1:
#            assert len(keys) > 0
#        if isinstance(_mpobject, dict):
#            for _k, _v in _mpobject.items():
#                break  # assume single k:v dict
#        else:
#            _v = Path(os.fsdecode(_mpobject)).resolve()
#        if verbose:
#            ic(index, _v)
#
#        with open(_v, "rb") as fh:
#            path_bytes_data = fh.read()
#
#        output(
#            path, reason=_mpobject, dict_output=dict_output, tty=tty, verbose=verbose
#        )
