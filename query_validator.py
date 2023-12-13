from utils import (
                    tokenize_query,
                    extract_from_clause,
                    extract_where_clause,
                    validate_select_clause, 
                    validate_from_clause, 
                    validate_where_clause
                )
import re
def validate_sub_query(sql_tokens):
    
    
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

def validate_query(sql_query):
    sql_tokens = tokenize_query(sql_query)
    
    sub_query_tokens = []
    
    # Split the query based on set operators 
    # i.e., union, intersection, set difference
    sub_query_token = []
    
    for token in sql_tokens:
        if token not in ['EXCEPT','INTERSECT','UNION']:
            sub_query_token.append(token)
        else:
            sub_query_tokens.append(sub_query_token)
            sub_query_token = []
            
    sub_query_tokens.append(sub_query_token)
    
    # Set operator must have two operands
    if [] in sub_query_tokens:
        return False
    
    # There may not be any set operators.
    if len(sub_query_tokens) == 1:
        return validate_sub_query(sql_tokens)
    
    sub_query_validation_results = []
    for tokens in sub_query_tokens:
        sub_query_validation_results += [validate_sub_query(tokens)]
    
    return all(sub_query_validation_results)
    
__all__ = ['validate_query']
