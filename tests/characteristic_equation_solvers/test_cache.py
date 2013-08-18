from nose.tools import eq_, raises
from nose_extra_tools import assert_is, assert_not_in #@UnresolvedImport
import os
import shutil
import tempfile
from beam_integrals import characteristic_equation_solvers as ces
from beam_integrals import exceptions as exc
from beam_integrals.beam_types import SimplySupportedBeam


class TestBestRootsCache(object):
    def setup(self):
        self.beam_type = SimplySupportedBeam()
        
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
            mode if mode is not None else self.max_mode,
            decimal_precision or self.decimal_precision,
            use_cache=True,
            cache_instance=self.cache
        )
    
    @raises(exc.UnableToLoadBestRootsCacheError)
    def test_unable_to_load_best_roots_cache_error(self):
        self.find_best_root()
    
    @raises(exc.InvalidModeError)
    def test_invalid_mode_error(self):
        self.regenerate_cache()
        
        self.find_best_root(mode=0)
    
    @raises(exc.BeamTypeNotFoundInCacheError)
    def test_beam_type_not_found_in_cache_error(self):
        self.regenerate_cache()
        self.cache._load_disk_cache(self.decimal_precision)
        
        del self.cache._ram_cache[self.decimal_precision][self.beam_type.id]
        self.find_best_root()
    
    @raises(exc.ModeNotFoundInCacheError)
    def test_mode_not_found_in_cache_error(self):
        self.regenerate_cache()
        
        self.find_best_root(mode=self.max_mode+1)
    
    @raises(exc.UnableToLoadBestRootsCacheError)
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
    
    def test_mode_list_ordering(self):
        self.regenerate_cache()
        self.cache._load_disk_cache(self.decimal_precision)
        
        beam_type_id_to_best_roots = self.cache._ram_cache[self.decimal_precision]
        for mode_list in beam_type_id_to_best_roots.values():
            eq_(mode_list, sorted(mode_list))
