class VariableRegistry:
    """Symbol table for managing variable information"""
    
    def __init__(self):
        self.entries = {}
        self.contexts = ['main']
        
    def add(self, identifier, var_type, initial_val=None, ctx=None):
        """
        Add a new variable to the symbol table
        
        Args:
            identifier: Variable name
            var_type: Data type (int, float, etc.)
            initial_val: Initial value (optional)
            ctx: Context/scope (optional, defaults to current context)
        """
        ctx = ctx or self.contexts[-1]
        key = f"{ctx}:{identifier}"
        self.entries[key] = {
            'id': identifier,
            'dtype': var_type,
            'val': initial_val,
            'ctx': ctx
        }
    
    def find(self, identifier):
        """
        Look up a variable in the symbol table
        
        Args:
            identifier: Variable name to find
            
        Returns:
            dict: Variable information or None if not found
        """
        for ctx in reversed(self.contexts):
            key = f"{ctx}:{identifier}"
            if key in self.entries:
                return self.entries[key]
        return None
    
    def all_entries(self):
        """
        Get all entries in the symbol table
        
        Returns:
            list: All variable entries
        """
        return list(self.entries.values())
    
    def push_context(self, context_name):
        """Push a new scope context"""
        self.contexts.append(context_name)
    
    def pop_context(self):
        """Pop the current scope context"""
        if len(self.contexts) > 1:
            self.contexts.pop()