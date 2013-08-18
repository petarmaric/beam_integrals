from itertools import chain, combinations
from nose_extra_tools import assert_in, assert_not_in #@UnresolvedImport
from beam_integrals.integrals import BaseIntegral, BaseIntegralWithSymetricVariables


MAX_MODE = 10 # Lower than defaults to speed up tests


def gen_integral_variable_combinations(min_len=1):
    all_vars = BaseIntegral.used_variables
    return chain.from_iterable(
        combinations(all_vars, r)
        for r in range(min_len, len(all_vars)+1)
    )

def setup():
    global plain_integral, integral_with_symetric_variables
    
    class I9001(BaseIntegral):
        pass
    plain_integral = I9001()
    
    class I9002(BaseIntegralWithSymetricVariables):
        pass
    integral_with_symetric_variables = I9002()

def teardown():
    type(plain_integral)._unregister_plugin()
    type(integral_with_symetric_variables)._unregister_plugin()

def test_plain_integral():
    for used_variables in gen_integral_variable_combinations():
        yield check_plain_integral, used_variables

def check_plain_integral(used_variables):
    integral = plain_integral
    integral.used_variables = used_variables
    
    keys_seen = set()
    for variables in integral.iterate_over_used_variables(max_mode=MAX_MODE):
        key = integral.cache_key(*variables, max_mode=MAX_MODE)
        assert_not_in(key, keys_seen) # Should be a cache miss
        keys_seen.add(key)

def test_integral_with_symetric_variables():
    for used_variables in gen_integral_variable_combinations(min_len=2):
        yield check_integral_with_symetric_variables, used_variables

def check_integral_with_symetric_variables(used_variables):
    integral = integral_with_symetric_variables
    integral.used_variables = used_variables
    
    keys_seen = set()
    sorted_variables_seen = set()
    for variables in integral.iterate_over_used_variables(max_mode=MAX_MODE):
        key = integral.cache_key(*variables, max_mode=MAX_MODE)
        sorted_variables = tuple(sorted(variables))
        if sorted_variables in sorted_variables_seen:
            assert_in(key, keys_seen) # Should be a cache hit
        else:
            assert_not_in(key, keys_seen) # Should be a cache miss
            keys_seen.add(key)
            sorted_variables_seen.add(sorted_variables)
