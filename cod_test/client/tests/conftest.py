import django.template.context
# import copy


# Monkeypatch BaseContext.__copy__ to fix Python 3.14 compatibility
# The original implementation uses copy(super()) which returns a 'super' object 
# in Python 3.14 instead of the instance, causing AttributeError.

def fixed_copy(self):
    # Create a new instance of the class without calling __init__
    duplicate = self.__class__.__new__(self.__class__)
    
    # Copy standard attributes
    if hasattr(self, '__dict__'):
        duplicate.__dict__ = self.__dict__.copy()
        
    # Specific handling for BaseContext.dicts
    # We need a new list containing the same dicts
    if hasattr(self, 'dicts'):
        duplicate.dicts = self.dicts[:]
        
    return duplicate

# Apply the patch
django.template.context.BaseContext.__copy__ = fixed_copy
