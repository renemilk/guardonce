# -*- coding: utf-8 -*-
# Copyright (C) 2016-2017 Cordell Bloor
# Published under the MIT License

from nose.tools import *
import guardonce.util as go

def test_ok():
    contents = '''
#ifndef MATCH_H
#define MATCH_H
'''
    g,s,e = go.guess_guard(contents)
    assert_equals(g, 'MATCH_H')
    assert_equals(s, 1)
    assert_equals(e, 32)

def test_ok_space_before_hash():
    contents = '''
 #ifndef MATCH_H
#define MATCH_H
'''
    g,s,e = go.guess_guard(contents)
    assert_equals(g, 'MATCH_H')
    assert_equals(s, 1)
    assert_equals(e, 33)

def test_ok_space_after_hash():
    contents = '''
# ifndef MATCH_H
# define MATCH_H
'''
    g,s,e = go.guess_guard(contents)
    assert_equals(g, 'MATCH_H')
    assert_equals(s, 1)
    assert_equals(e, 34)

@raises(ValueError)
def test_no_ifndef():
    contents = '''
#ifdef MATCH_H
#define MATCH_H
'''
    go.guess_guard(contents)

@raises(ValueError)
def test_no_define():
    contents = '''
#ifndef MATCH_H
#defne MATCH_H
'''
    go.guess_guard(contents)

@raises(ValueError)
def test_mismatched_define_symbol():
    contents = '''
#ifndef MATCH_H
#define MISMATCH_H
'''
    go.guess_guard(contents)

@raises(ValueError)
def test_extra_junk_on_ifndef():
    contents = '''
#ifndef MATCH_H WEIRD_HUH
#define MATCH_H
'''
    go.guess_guard(contents)

@raises(ValueError)
def test_extra_junk_on_define():
    contents = '''
#ifndef MATCH_H
#define MATCH_H WEIRD_HUH
'''
    go.guess_guard(contents)

def test_extra_whitespace_on_ifndef():
    contents = '''
#ifndef MATCH_H 
#define MATCH_H
'''
    g,s,e = go.guess_guard(contents)
    assert_equals(g, 'MATCH_H')
    assert_equals(s, 1)
    assert_equals(e, 33)

def test_extra_whitespace_on_define():
    contents = '''
#ifndef MATCH_H
#define MATCH_H 
'''
    g,s,e = go.guess_guard(contents)
    assert_equals(g, 'MATCH_H')
    assert_equals(s, 1)
    assert_equals(e, 33)

def test_define_with_value_1():
    contents = '''
#ifndef MATCH_H
#define MATCH_H 1
'''
    g,s,e = go.guess_guard(contents)
    assert_equals(g, 'MATCH_H')
    assert_equals(s, 1)
    assert_equals(e, 34)

@raises(ValueError)
def test_define():
    contents = '''
#ifndef ONE
#define ONE 1
#endif
'''
    go.guess_guard(contents)

@raises(ValueError)
def test_define_with_space():
    contents = '''
#ifndef ONE
#define ONE 1
 
#endif
'''
    go.guess_guard(contents)
