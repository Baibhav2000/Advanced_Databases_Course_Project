from utils import (
                    tokenize_query,
                    extract_from_clause,
                    extract_where_clause,
                    validate_select_clause, 
                    validate_from_clause, 
                    validate_where_clause
                )

def validate_query(sql_query):
    sql_tokens = tokenize_query(sql_query)
    
    # An SQL query must have a SELECT and a FROM clause
    if 'SELECT' not in sql_tokens or 'FROM' not in sql_tokens:
        return False
    
    # The SELECT keyword must be the first token
    if sql_tokens[0] != 'SELECT':
        return False
    
    where_keyword_pos = len(sql_tokens)
    where_clause_tokens = []
    
    # Extract WHERE Clause tokens
    if 'WHERE' in sql_tokens:
        where_keyword_pos = sql_tokens.index('WHERE')
        where_clause_tokens.extend(extract_where_clause(sql_tokens,where_keyword_pos))
        
    from_keyword_pos = sql_tokens.index('FROM')
    from_clause_tokens = extract_from_clause(sql_tokens,from_keyword_pos,where_keyword_pos)
    select_clause_tokens = sql_tokens[1:from_keyword_pos]
    
    if "WHERE" in sql_tokens:
        return (validate_select_clause(select_clause_tokens)
                and validate_from_clause(from_clause_tokens) and validate_where_clause(where_clause_tokens))
    else:
        return validate_select_clause(select_clause_tokens) and validate_from_clause(from_clause_tokens)
    
__all__ = ['validate_query']
