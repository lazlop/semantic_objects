"""
Test that get_related_classes works correctly regardless of import source.
This addresses the issue where the function didn't work when imported from core.py
but worked when imported from s223 module.
"""
import sys
sys.path.append('..')

# Test 1: Import from core module
from src.semantic_objects.core import get_related_classes as get_related_classes_from_core

# Test 2: Import from s223 module  
from src.semantic_objects.s223 import get_related_classes as get_related_classes_from_s223

# Import a sample s223 class to test with
from src.semantic_objects.s223.entities import Space

def test_import_from_core():
    """Test that get_related_classes works when imported from core module."""
    predicate_lst, entity_lst = get_related_classes_from_core(Space)
    
    print("Test 1: Import from core module")
    print(f"  Predicates found: {len(predicate_lst)}")
    print(f"  Entities found: {len(entity_lst)}")
    
    # Should find at least some classes
    assert len(predicate_lst) > 0 or len(entity_lst) > 0, \
        "Should find at least some related classes when imported from core"
    
    print("  ✓ PASSED: Found related classes when imported from core\n")
    return predicate_lst, entity_lst

def test_import_from_s223():
    """Test that get_related_classes works when imported from s223 module."""
    predicate_lst, entity_lst = get_related_classes_from_s223(Space)
    
    print("Test 2: Import from s223 module")
    print(f"  Predicates found: {len(predicate_lst)}")
    print(f"  Entities found: {len(entity_lst)}")
    
    # Should find at least some classes
    assert len(predicate_lst) > 0 or len(entity_lst) > 0, \
        "Should find at least some related classes when imported from s223"
    
    print("  ✓ PASSED: Found related classes when imported from s223\n")
    return predicate_lst, entity_lst

def test_consistency():
    """Test that both import methods return the same results."""
    core_predicates, core_entities = test_import_from_core()
    s223_predicates, s223_entities = test_import_from_s223()
    
    print("Test 3: Consistency check")
    print(f"  Core predicates: {len(core_predicates)}, S223 predicates: {len(s223_predicates)}")
    print(f"  Core entities: {len(core_entities)}, S223 entities: {len(s223_entities)}")
    
    # Both should return the same number of classes
    assert len(core_predicates) == len(s223_predicates), \
        f"Predicate counts should match: core={len(core_predicates)}, s223={len(s223_predicates)}"
    assert len(core_entities) == len(s223_entities), \
        f"Entity counts should match: core={len(core_entities)}, s223={len(s223_entities)}"
    
    print("  ✓ PASSED: Both import methods return consistent results\n")

def test_class_method():
    """Test that the new class method works directly."""
    predicate_lst, entity_lst = Space.get_related_classes()
    
    print("Test 4: Direct class method call")
    print(f"  Predicates found: {len(predicate_lst)}")
    print(f"  Entities found: {len(entity_lst)}")
    
    # Should find at least some classes
    assert len(predicate_lst) > 0 or len(entity_lst) > 0, \
        "Should find at least some related classes using class method"
    
    print("  ✓ PASSED: Class method works correctly\n")

if __name__ == "__main__":
    print("=" * 60)
    print("Testing get_related_classes import fix")
    print("=" * 60 + "\n")
    
    try:
        test_consistency()
        test_class_method()
        
        print("=" * 60)
        print("ALL TESTS PASSED! ✓")
        print("=" * 60)
        print("\nThe fix successfully resolves the import issue.")
        print("get_related_classes now works the same regardless of import source.")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        raise
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        raise
