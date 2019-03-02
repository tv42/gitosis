from nose.tools import eq_ as eq, assert_raises

from gitosis import group, util
from gitosis.test.util import partial_next

def test_no_emptyConfig():
    cfg = util.RawConfigParser()
    gen = group.getMembership(config=cfg, user='jdoe')
    eq(next(gen), 'all')
    assert_raises(StopIteration, partial_next(gen))

def test_no_emptyGroup():
    cfg = util.RawConfigParser()
    cfg.add_section('group hackers')
    gen = group.getMembership(config=cfg, user='jdoe')
    eq(next(gen), 'all')
    assert_raises(StopIteration, partial_next(gen))

def test_no_notListed():
    cfg = util.RawConfigParser()
    cfg.add_section('group hackers')
    cfg.set('group hackers', 'members', 'wsmith')
    gen = group.getMembership(config=cfg, user='jdoe')
    eq(next(gen), 'all')
    assert_raises(StopIteration, partial_next(gen))

def test_yes_simple():
    cfg = util.RawConfigParser()
    cfg.add_section('group hackers')
    cfg.set('group hackers', 'members', 'jdoe')
    gen = group.getMembership(config=cfg, user='jdoe')
    eq(next(gen), 'hackers')
    eq(next(gen), 'all')
    assert_raises(StopIteration, partial_next(gen))

def test_yes_leading():
    cfg = util.RawConfigParser()
    cfg.add_section('group hackers')
    cfg.set('group hackers', 'members', 'jdoe wsmith')
    gen = group.getMembership(config=cfg, user='jdoe')
    eq(next(gen), 'hackers')
    eq(next(gen), 'all')
    assert_raises(StopIteration, partial_next(gen))

def test_yes_trailing():
    cfg = util.RawConfigParser()
    cfg.add_section('group hackers')
    cfg.set('group hackers', 'members', 'wsmith jdoe')
    gen = group.getMembership(config=cfg, user='jdoe')
    eq(next(gen), 'hackers')
    eq(next(gen), 'all')
    assert_raises(StopIteration, partial_next(gen))

def test_yes_middle():
    cfg = util.RawConfigParser()
    cfg.add_section('group hackers')
    cfg.set('group hackers', 'members', 'wsmith jdoe danny')
    gen = group.getMembership(config=cfg, user='jdoe')
    eq(next(gen), 'hackers')
    eq(next(gen), 'all')
    assert_raises(StopIteration, partial_next(gen))

def test_yes_recurse_one():
    cfg = util.RawConfigParser()
    cfg.add_section('group hackers')
    cfg.set('group hackers', 'members', 'wsmith @smackers')
    cfg.add_section('group smackers')
    cfg.set('group smackers', 'members', 'danny jdoe')
    gen = group.getMembership(config=cfg, user='jdoe')
    eq(next(gen), 'smackers')
    eq(next(gen), 'hackers')
    eq(next(gen), 'all')
    assert_raises(StopIteration, partial_next(gen))

def test_yes_recurse_one_ordering():
    cfg = util.RawConfigParser()
    cfg.add_section('group smackers')
    cfg.set('group smackers', 'members', 'danny jdoe')
    cfg.add_section('group hackers')
    cfg.set('group hackers', 'members', 'wsmith @smackers')
    gen = group.getMembership(config=cfg, user='jdoe')
    eq(next(gen), 'smackers')
    eq(next(gen), 'hackers')
    eq(next(gen), 'all')
    assert_raises(StopIteration, partial_next(gen))

def test_yes_recurse_three():
    cfg = util.RawConfigParser()
    cfg.add_section('group hackers')
    cfg.set('group hackers', 'members', 'wsmith @smackers')
    cfg.add_section('group smackers')
    cfg.set('group smackers', 'members', 'danny @snackers')
    cfg.add_section('group snackers')
    cfg.set('group snackers', 'members', '@whackers foo')
    cfg.add_section('group whackers')
    cfg.set('group whackers', 'members', 'jdoe')
    gen = group.getMembership(config=cfg, user='jdoe')
    eq(next(gen), 'whackers')
    eq(next(gen), 'snackers')
    eq(next(gen), 'smackers')
    eq(next(gen), 'hackers')
    eq(next(gen), 'all')
    assert_raises(StopIteration, partial_next(gen))

def test_yes_recurse_junk():
    cfg = util.RawConfigParser()
    cfg.add_section('group hackers')
    cfg.set('group hackers', 'members', '@notexist @smackers')
    cfg.add_section('group smackers')
    cfg.set('group smackers', 'members', 'jdoe')
    gen = group.getMembership(config=cfg, user='jdoe')
    eq(next(gen), 'smackers')
    eq(next(gen), 'hackers')
    eq(next(gen), 'all')
    assert_raises(StopIteration, partial_next(gen))

def test_yes_recurse_loop():
    cfg = util.RawConfigParser()
    cfg.add_section('group hackers')
    cfg.set('group hackers', 'members', '@smackers')
    cfg.add_section('group smackers')
    cfg.set('group smackers', 'members', '@hackers jdoe')
    gen = group.getMembership(config=cfg, user='jdoe')
    eq(next(gen), 'smackers')
    eq(next(gen), 'hackers')
    eq(next(gen), 'all')
    assert_raises(StopIteration, partial_next(gen))

def test_no_recurse_loop():
    cfg = util.RawConfigParser()
    cfg.add_section('group hackers')
    cfg.set('group hackers', 'members', '@smackers')
    cfg.add_section('group smackers')
    cfg.set('group smackers', 'members', '@hackers')
    gen = group.getMembership(config=cfg, user='jdoe')
    eq(next(gen), 'all')
    assert_raises(StopIteration, partial_next(gen))
