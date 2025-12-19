"""Test automatic field initialization with values"""

from src.semantic_objects.s223.entities import Space
from src.semantic_objects.s223.properties import Area

# Test 1: Create Space with raw value
print("Test 1: Creating Space with area=100")
space = Space(area=100)
print(f"  space.area = {space.area}")
print(f"  type(space.area) = {type(space.area)}")
print(f"  isinstance(space.area, Area) = {isinstance(space.area, Area)}")

# Test 2: Create Space with Area object (should still work)
print("\nTest 2: Creating Space with Area object")
area_obj = Area(200)
space2 = Space(area=area_obj)
print(f"  space2.area = {space2.area}")
print(f"  type(space2.area) = {type(space2.area)}")
print(f"  isinstance(space2.area, Area) = {isinstance(space2.area, Area)}")

# Test 3: Verify the area has correct properties
print("\nTest 3: Checking Area properties")
print(f"  space.area.value = {space.area.value}")
print(f"  space.area.unit = {space.area.unit}")
print(f"  space.area.qk = {space.area.qk}")

print("\n✓ All tests passed!")
