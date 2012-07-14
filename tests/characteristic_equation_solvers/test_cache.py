from nose.tools import raises
import os
import shutil
import tempfile
from beam_integrals import beam_types as bt
from beam_integrals import characteristic_equation_solvers as ces
from beam_integrals.exceptions import UnableToLoadBestRootsCacheError, ModeNotFoundInCacheError
from tests.tools import assert_is, assert_not_in #@UnresolvedImport


class TestBestRootsCache(object):
    def setup(self):
        self.beam_type = bt.SimplySupportedBeam()
        
        # Lower than defaults to speed up tests
        self.max_mode = 2 
        self.decimal_precision = 15
        
        self.disk_cache_dir = os.path.join(
            tempfile.mkdtemp(),
            'need-a-non-existant-directory-for-100-percent-code-coverage'
        )
        self.cache = ces.BestRootsCache(self.disk_cache_dir)
    
    def teardown(self):
        shutil.rmtree(self.disk_cache_dir)
    
    def regenerate_cache(self):
        self.cache.regenerate(self.max_mode, self.decimal_precision)
    
    def find_best_root(self, mode=None, decimal_precision=None):
        return ces.find_best_root(
            self.beam_type,
            mode or self.max_mode,
            decimal_precision or self.decimal_precision,
            use_cache=True,
            cache_instance=self.cache
        )
    
    @raises(UnableToLoadBestRootsCacheError)
    def test_unable_to_load_best_roots_cache_error(self):
        self.find_best_root()
    
    @raises(ModeNotFoundInCacheError)
    def test_mode_not_found_in_cache_error(self):
        self.regenerate_cache()
        
        self.find_best_root(mode=self.max_mode+1)
    
    @raises(UnableToLoadBestRootsCacheError)
    def test_different_decimal_precisions_dont_have_same_cache_key(self):
        self.regenerate_cache()
        
        self.find_best_root(decimal_precision=self.decimal_precision+1)
    
    def test_cached_find_best_root_returns_same_objects(self):
        self.regenerate_cache()
        
        cache_hit_1 = self.find_best_root()
        cache_hit_2 = self.find_best_root()
        assert_is(cache_hit_1, cache_hit_2)
    
    def test_ram_cache_cleared_after_regeneration(self):
        self.regenerate_cache()
        
        assert_not_in(self.decimal_precision, self.cache._ram_cache)
