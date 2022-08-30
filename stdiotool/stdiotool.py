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

# code style:
#   avoid guessing on spelling, just write the word out
#   dont_makedirs -> no_makedirs
#   no guessing on case: local vars, functions and methods are lower case. classes are ThisClass(). Globals are THIS.
#   del vars explicitely ASAP, assumptions are buggy
#   rely on the compiler, code verbosity and explicitness can only be overruled by benchamrks (are really compiler bugs)
#   no tabs. code must display the same independent of viewer
#   no recursion, recursion is undecidiable, randomly bounded, and hard to reason about
#   each elementis the same, no special cases for the first or last elemetnt:
#       [1, 2, 3,] not [1, 2, 3]
#       def this(*.
#                a: bool,
#                b: bool,
#               ):
#
#   expicit loop control is better than while (condition):
#       while True:
#           # continue/break explicit logic
#   only computer generated commit messages _should_ start with a cap letter


# TODO:
#   https://github.com/kvesteri/validators
import os
import sys
import click
import time
import logging
import sh
from collections.abc import Sequence
from clicktool import click_add_options, click_global_options
from click_auto_help import AHGroup
from signal import signal, SIGPIPE, SIG_DFL
from pathlib import Path
from mptool import output
from mptool import mpd_enumerate
from clicktool import tv
from asserttool import validate_slice
from eprint import eprint
from asserttool import ic
from retry_on_exception import retry_on_exception
from timetool import get_timestamp

from unmp import unmp
##from typing import Tuple
#from typing import Generator
#from typing import ByteString
#from with_sshfs import sshfs
#from with_chdir import chdir
#from collections import defaultdict
#from prettyprinter import cpprint
#from prettyprinter import install_extras
#install_extras(['attrs'])
#from configtool import click_read_config
#from configtool import click_write_config_entry
#from asserttool import not_root
#from pathtool import path_is_block_special
#from pathtool import write_line_to_file
#from getdents import files
#from prettytable import PrettyTable
#output_table = PrettyTable()


sh.mv = None  # use sh.busybox('mv'), coreutils ignores stdin read errors

logging.basicConfig(level=logging.INFO)

# click-command-tree
#from click_plugins import with_plugins
#from pkg_resources import iter_entry_points

# import pdb; pdb.set_trace()
# #set_trace(term_size=(80, 24))
# from pudb import set_trace; set_trace(paused=False)

##def log_uncaught_exceptions(ex_cls, ex, tb):
##   eprint(''.join(traceback.format_tb(tb)))
##   eprint('{0}: {1}'.format(ex_cls, ex))
##
##sys.excepthook = log_uncaught_exceptions

#this should be earlier in the imports, but isort stops working
signal(SIGPIPE, SIG_DFL)


# @with_plugins(iter_entry_points('click_command_tree'))
# @click.group(no_args_is_help=True, cls=AHGroup)
# @click_add_options(click_global_options)
# @click.pass_context
# def cli(ctx,
#         verbose: bool | int | float,
#         verbose_inf: bool,
#         dict_output: bool,
#         ) -> None:
#
#     tty, verbose = tv(ctx=ctx,
#                       verbose=verbose,
#                       verbose_inf=verbose_inf,
#                       )


# update setup.py if changing function name
#@click.argument("slice_syntax", type=validate_slice, nargs=1)
@click.command()
@click.argument('keys', type=str, nargs=-1)
@click.argument("sysskel",
                type=click.Path(exists=False,
                                dir_okay=True,
                                file_okay=False,
                                allow_dash=False,
                                path_type=Path,),
                nargs=1,
                required=True,)
@click.option('--ipython', is_flag=True)
@click_add_options(click_global_options)
@click.pass_context
def cli(ctx,
        keys: Sequence[str],
        sysskel: Path,
        ipython: bool,
        verbose: bool | int | float,
        verbose_inf: bool,
        dict_output: bool,
        ) -> None:

    tty, verbose = tv(ctx=ctx,
                      verbose=verbose,
                      verbose_inf=verbose_inf,
                      )

    iterator: Sequence[dict | bytes] = unmp(valid_types=[dict, bytes,], verbose=verbose)

    # need to send a single key, or multiple keys, if multiple keys, keys need to specified on the commandline
    # either way, the output is still a dict

    index = 0
    _k = None
    for index, _mpobject, key_count in mpd_enumerate(iterator, verbose=verbose):
        #if index == 0:
        #    first_type = type(_mpobject)
        #    if first_type == dict:
        #        key_count = len(list(_mpobject.keys()))
        #    else:
        #        key_count = None
        if key_count > 1:
            assert len(keys) > 0
        if isinstance(_mpobject, dict):
            for _k, _v in _mpobject.items():
                break   # assume single k:v dict
        else:
            _v = Path(os.fsdecode(_mpobject)).resolve()
        if verbose:
            ic(index, _v)

        with open(_v, 'rb') as fh:
            path_bytes_data = fh.read()

        output(path, reason=_mpobject, dict_output=dict_output, tty=tty, verbose=verbose)

#        if ipython:
#            import IPython; IPython.embed()

if __name__ == '__main__':
    # pylint: disable=E1120
    cli()

#!/usr/bin/env python3
# -*- coding: utf8 -*-

# pylint: disable=missing-docstring               # [C0111] docstrings are always outdated and wrong
# pylint: disable=missing-module-docstring        # [C0114]
# pylint: disable=fixme                           # [W0511] todo is encouraged
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

# import gpib
# import visa
# import pyvisa as visa  # conflct with https://github.com/visa-sdk/visa-python
# from pyvisa.errors import VisaIOError
# from gpib import GpibError

from __future__ import annotations

import os
import sys
from contextlib import contextmanager
from signal import SIG_DFL
from signal import SIGPIPE
from signal import signal

import click
import pyvisa
import sh
from asserttool import ic
from bnftool import get_bnf_syntax
from click_auto_help import AHGroup
from clicktool import click_add_options
from clicktool import click_global_options
from clicktool import tv
from mptool import output
from pyvisa.errors import VisaIOError

signal(SIGPIPE, SIG_DFL)


# https://github.com/pyvisa/pyvisa-py/issues/282
@contextmanager
def _supress_stderr():
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


class NoResourcesFoundError(ValueError):
    pass


def get_instrument(
    *,
    address: str,
    verbose: bool | int | float,
):

    if verbose:
        ic(address)
    rm = pyvisa.ResourceManager("@py")
    ic(address)
    inst = rm.open_resource(address)
    return inst


def command_query(
    *,
    address: str,
    command: str,
    verbose: bool | int | float,
):

    ic(address)
    inst = get_instrument(
        address=address,
        verbose=verbose,
    )
    # idn = inst.query("*IDN?")
    idn = inst.query(command)
    if verbose:
        ic(idn)
    return idn.strip()


def command_idn(
    *,
    address: str,
    verbose: bool | int | float,
):

    idn = command_query(address=address, command="*IDN?", verbose=verbose)
    # inst = get_instrument(address=address, verbose=verbose,)
    # idn = inst.query("*IDN?")
    # if verbose:
    #    ic(idn)
    # return idn.strip()
    return idn


def get_resources(
    verbose: bool | int | float,
):

    with _supress_stderr():
        resource_manager = pyvisa.ResourceManager()
        resources = list(resource_manager.list_resources())

    if verbose:
        ic(resources)
    try:
        resources.remove("ASRL/dev/ttyS0::INSTR")
    except ValueError:
        pass

    if resources:
        return tuple(resources)
    else:
        raise NoResourcesFoundError


@click.group(no_args_is_help=True, cls=AHGroup)
@click_add_options(click_global_options)
@click.pass_context
def cli(
    ctx,
    verbose: bool | int | float,
    verbose_inf: bool,
    dict_output: bool,
):

    tty, verbose = tv(
        ctx=ctx,
        verbose=verbose,
        verbose_inf=verbose_inf,
    )


@cli.command("idn")
@click.argument("address", type=str)
@click_add_options(click_global_options)
@click.pass_context
def _read_command_idn(
    ctx,
    address: str,
    verbose: bool | int | float,
    verbose_inf: bool,
    dict_output: bool,
):

    tty, verbose = tv(
        ctx=ctx,
        verbose=verbose,
        verbose_inf=verbose_inf,
    )

    print(command_idn(address=address, verbose=verbose))


@cli.command("info")
@click_add_options(click_global_options)
@click.pass_context
def _pyvisa_info(
    ctx,
    verbose: bool | int | float,
    verbose_inf: bool,
    dict_output: bool,
):

    tty, verbose = tv(
        ctx=ctx,
        verbose=verbose,
        verbose_inf=verbose_inf,
    )

    info_command = sh.Command("/usr/bin/pyvisa-info")
    # python -c "from pyvisa import util; util.get_debug_info()"
    info_command(_out=sys.stdout)


@cli.command("syntax")
@click_add_options(click_global_options)
@click.pass_context
def _bnf_syntax(
    ctx,
    verbose: bool | int | float,
    verbose_inf: bool,
    dict_output: bool,
):

    tty, verbose = tv(
        ctx=ctx,
        verbose=verbose,
        verbose_inf=verbose_inf,
    )

    bnf_symbols = get_bnf_syntax()
    command_message_elements = {
        "<Header>": "This is the basic command name. If the header ends with a question mark, the command is a query. The header may begin with a colon (:) character. If the command is concatenated with other commands, the beginning colon is required. Never use the beginning colon with command headers beginning with a star (*).",
        "<Mnenomic>": "This is a header subfunction. Some command headers have only one mnemonic. If a command header has multiple mnemonics, a colon (:) character always separates them from each other.",
        "<Argument>": "This is a quantity, quality, restriction, or limit associated with the header. Some commands have no arguments while others have multiple arguments. A <space> separates arguments from the header. A <comma> separates arguments from each other.",
        "<Comma>": "A single comma is used between arguments of multiple-argument commands. Optionally, there may be white space characters before and after the comma.",
        "<Space>": "A white space character is used between a command header and the related argument. Optionally, a white space may consist of multiple white space characters.",
    }
    command = "[:]<Header>[<Space><Argument>[<Comma> <Argument>]...]"
    query = ("[:]<Header>", "[:]<Header>[<Space><Argument> [<Comma><Argument>]...]")

    output(bnf_symbols, reason=None, dict_output=dict_output, tty=tty, verbose=verbose)
    output(
        command_message_elements,
        reason=None,
        dict_output=dict_output,
        tty=tty,
        verbose=verbose,
    )
    output(command, reason=None, dict_output=dict_output, tty=tty, verbose=verbose)
    output(query, reason=None, dict_output=dict_output, tty=tty, verbose=verbose)


@cli.command("command-write")
@click.argument("address", type=str)
@click.argument("command", type=str)
@click_add_options(click_global_options)
@click.pass_context
def _command_write(
    ctx,
    address: str,
    command: str,
    verbose: bool | int | float,
    verbose_inf: bool,
    dict_output: bool,
):

    tty, verbose = tv(
        ctx=ctx,
        verbose=verbose,
        verbose_inf=verbose_inf,
    )

    inst = get_instrument(
        address=address,
        verbose=verbose,
    )
    if verbose:
        ic(command, len(command))
    result = inst.write(command)
    print(result)


@cli.command("command-query")
@click.argument("address", type=str)
@click.argument("command", type=str)
@click_add_options(click_global_options)
@click.pass_context
def _command_query(
    ctx,
    address: str,
    command: str,
    verbose: bool | int | float,
    verbose_inf: bool,
    dict_output: bool,
):

    tty, verbose = tv(
        ctx=ctx,
        verbose=verbose,
        verbose_inf=verbose_inf,
    )

    inst = get_instrument(
        address=address,
        verbose=verbose,
    )
    if verbose:
        ic(command, len(command))
    result = inst.query(command)
    print(result)


@cli.command("addresses")
@click.option("--ipython", is_flag=True)
@click_add_options(click_global_options)
@click.pass_context
def _list_addresses(
    ctx,
    verbose: bool | int | float,
    verbose_inf: bool,
    dict_output: bool,
    ipython: bool,
):

    tty, verbose = tv(
        ctx=ctx,
        verbose=verbose,
        verbose_inf=verbose_inf,
    )

    # https://github.com/pyvisa/pyvisa-py/issues/282
    with _supress_stderr():
        resources = get_resources(verbose=verbose)
    if verbose:
        ic(resources)
    for resource in resources:
        output(resource, reason=None, tty=tty, dict_output=dict_output, verbose=verbose)


@cli.command("idns")
@click.option("--ipython", is_flag=True)
@click_add_options(click_global_options)
@click.pass_context
def _list_idns(
    ctx,
    verbose: bool | int | float,
    verbose_inf: bool,
    dict_output: bool,
    ipython: bool,
):

    # forcing dict_output=True since a IDN alone is _never_ as useful as a (GPIB source: IDN) mapping
    # toodoo-maybe: if the GPIB source was read on stdin, this wouldnt be be necessary
    dict_output = True  # this does not take input on stdin, todo: fix dict_output convention to reflect this
    tty, verbose = tv(
        ctx=ctx,
        verbose=verbose,
        verbose_inf=verbose_inf,
    )

    if verbose:
        ic('calling: pyvisa.ResourceManager("@py")')
    with _supress_stderr():
        rm = pyvisa.ResourceManager("@py")

    if verbose:
        ic("calling: get_resources()")
    resources = get_resources(verbose=verbose)
    for resource in resources:
        if verbose:
            ic(resource)
        inst = rm.open_resource(resource)
        if verbose:
            ic(inst)
        try:
            output(
                inst.query("*IDN?"),
                reason=resource,
                tty=tty,
                verbose=verbose,
                dict_output=dict_output,
            )
        except VisaIOError as e:
            if verbose:
                ic(e)
            if not e.args[0].endswith("Timeout expired before operation completed."):
                raise e
