# Copyright (c) 2015 BalaBit
# All Rights Reserved.

pytest_plugins = "pytester"


def test_invalid_debian_package_name_cannot_be_fetched(cmd, initproj):
    initproj("debian123-0.42", filedefs={
        'tox.ini': '''
            [testenv]
            debian_deps=
              no-such-debian-package=123.42
        '''
    })
    result = cmd("tox")
    assert "E: Unable to locate package no-such-debian-package" in result.out
    assert result.ret


def test_debian_package_will_be_extracted_into_virtual_env(cmd, initproj):
    initproj("debian123-0.56", filedefs={
        'tox.ini': '''
            [testenv]
            debian_deps=
              graphviz
            commands= ls -1 .tox/python/bin
        '''
    })
    result = cmd("tox")
    assert "dot" in result.out
    assert result.ret == 0


def test_can_extract_multiple_packages(cmd, initproj):
    initproj("debian123-0.56", filedefs={
        'tox.ini': '''
            [testenv]
            debian_deps=
              graphviz
              vim
            commands= ls -1 .tox/python/bin
        '''
    })
    result = cmd("tox")
    assert "dot" in result.out
    assert "vim" in result.out
    assert result.ret == 0


def test_empty_debian_dependency_dont_call_apt_get(cmd, initproj):
    initproj("debian123-0.56", filedefs={
        'tox.ini': '''
            [testenv]
            debian_deps=
        '''
    })
    result = cmd("tox")
    assert 'apt-get' not in result.out
    assert result.ret == 0


def test_can_pass_additional_options_to_apt_get(cmd, initproj):
    initproj("debian123-0.56", filedefs={
        'tox.ini': '''
            [testenv]
            apt_opts=
              --no-such-option
            debian_deps=
              graphviz
        '''
    })
    result = cmd("tox")
    assert "no-such-option" in result.out
    assert result.ret


def test_install3_logs_its_actions(cmd, initproj):
    assert_logs_actions(cmd, initproj, "py3")


def assert_logs_actions(cmd, initproj, venv_name):
    initproj("debian123-0.56", filedefs={
        'tox.ini': '''
            [tox]
            envlist={venv_name}
            [testenv]
            debian_deps=
              vim
              graphviz
        '''.format(venv_name=venv_name)
    })
    result = cmd("tox")
    assert "{} apt-get download: vim, graphviz".format(venv_name) in result.out
    assert "{} dpkg extract: graphviz".format(venv_name) in result.out
    assert "{} dpkg extract: vim".format(venv_name) in result.out
    assert result.ret == 0
