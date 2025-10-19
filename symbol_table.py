class VariableRegistry:
    """Symbol table for managing variable information with proper scope handling"""
    
    def __init__(self):
        self.scope_stack = [{}]  # Stack of scope dictionaries
        self.scope_names = ['global']  # Track scope names for debugging
        self.current_scope_id = 0
        
    def add(self, identifier, var_type, initial_val=None, context='declaration'):
        """
        Add a new variable to the current scope
        
        Args:
            identifier: Variable name
            var_type: Data type (int, float, etc.)
            initial_val: Initial value (optional)
            context: Context of variable (declaration, assignment, etc.)
        """
        current_scope = self.scope_stack[-1]
        current_scope[identifier] = {
            'id': identifier,
            'dtype': var_type,
            'val': initial_val,
            'ctx': context,
            'scope': self.scope_names[-1],
            'scope_level': len(self.scope_stack) - 1
        }
    
    def find(self, identifier):
        """
        Look up a variable in the symbol table (searches from current scope up to global)
        
        Args:
            identifier: Variable name to find
            
        Returns:
            dict: Variable information or None if not found
        """
        # Search from current scope up to global scope
        for scope in reversed(self.scope_stack):
            if identifier in scope:
                return scope[identifier]
        return None
    
    def find_in_current_scope(self, identifier):
        """
        Look up a variable only in the current scope
        
        Args:
            identifier: Variable name to find
            
        Returns:
            dict: Variable information or None if not found in current scope
        """
        current_scope = self.scope_stack[-1]
        return current_scope.get(identifier)
    
    def update(self, identifier, new_value):
        """
        Update the value of an existing variable (doesn't change context)
        
        Args:
            identifier: Variable name to update
            new_value: New value to assign
            
        Returns:
            bool: True if variable was found and updated, False otherwise
        """
        # Search from current scope up to global scope
        for scope in reversed(self.scope_stack):
            if identifier in scope:
                scope[identifier]['val'] = new_value
                # Keep original context (declaration)
                return True
        return False
    
    def all_entries(self):
        """
        Get all entries in all scopes
        
        Returns:
            list: All variable entries with scope information
        """
        all_vars = []
        for i, scope in enumerate(self.scope_stack):
            for var_info in scope.values():
                all_vars.append(var_info)
        return all_vars
    
    def current_scope_entries(self):
        """
        Get all entries in the current scope only
        
        Returns:
            list: Variables in current scope
        """
        current_scope = self.scope_stack[-1]
        return list(current_scope.values())
    
    def push_scope(self, scope_name=None):
        """
        Push a new scope onto the stack
        
        Args:
            scope_name: Optional name for the scope (for debugging)
        """
        if scope_name is None:
            self.current_scope_id += 1
            scope_name = f"scope_{self.current_scope_id}"
        
        self.scope_stack.append({})
        self.scope_names.append(scope_name)
    
    def pop_scope(self):
        """
        Pop the current scope from the stack
        
        Returns:
            dict: The popped scope or None if only global scope remains
        """
        if len(self.scope_stack) > 1:
            popped_scope = self.scope_stack.pop()
            self.scope_names.pop()
            return popped_scope
        return None
    
    def get_scope_level(self):
        """
        Get the current scope level (0 = global, 1 = first nested, etc.)
        
        Returns:
            int: Current scope level
        """
        return len(self.scope_stack) - 1
    
    def get_current_scope_name(self):
        """
        Get the name of the current scope
        
        Returns:
            str: Current scope name
        """
        return self.scope_names[-1]
    
    def is_declared_in_current_scope(self, identifier):
        """
        Check if a variable is declared in the current scope
        
        Args:
            identifier: Variable name to check
            
        Returns:
            bool: True if variable exists in current scope
        """
        return identifier in self.scope_stack[-1]
    
    def clear(self):
        """Clear all scopes and reset to global scope only"""
        self.scope_stack = [{}]
        self.scope_names = ['global']
        self.current_scope_id = 0
