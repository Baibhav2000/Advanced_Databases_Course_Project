import re
from functools import reduce

keywords = [
            'SELECT', 
            'FROM', 
            'WHERE', 
            'LEFT',
            'RIGHT',
            'FULL',
            'INNER',
            'JOIN',
            'AND',
            'OR',
            'ON',
            'EXCEPT',
            'UNION',
            'INTERSECTION'
        ]

relational_operators = ['<', '>', '=', '!=', '>=', '<=']

rel_alg_operators = {
    "SELECT"     : "\u220f",
    "WHERE"      : "\u03c3",
    "INNER"      : "\u2a1d",
    "JOIN"       : "\u2a1d",
    "LEFT"       : "\u27d5",
    "RIGHT"      : "\u27d6",
    "FULL"       : "\u27d7",
    "UNION"      : "\u222a",
    "INTERSECT"  : "\u2229",
    "EXCEPT"     : "\u2212",
    "AND"        : "\u22c0",
    "OR"         : "\u22c1"
}

def extract_from_clause(sql_tokens, from_keyword_pos, where_keyword_pos):
    return sql_tokens[from_keyword_pos + 1 : where_keyword_pos]

def extract_where_clause(sql_tokens, where_keyword_pos):
    return sql_tokens[where_keyword_pos + 1:]

def validate_field_name(name):
    name_pattern = r'\w+(\.\w+)?'
    
    return re.fullmatch(name_pattern,name) and name not in keywords

def validate_table_name(name):
    name_pattern = r'\w+'
    
    return re.fullmatch(name_pattern,name) and name not in keywords

def validate_numeric_constant(token):
    return re.match(r'\d+',token) is not None

def validate_string_literal(token):
    return re.match(r'^([\'"]).*\1$',token) is not None

def validate_relational_expression(tokens):
    if len(tokens) != 3:
        return False
    
    return (validate_field_name(tokens[0]) and 
                (validate_string_literal(tokens[-1]) or validate_numeric_constant(tokens[-1]) or
                 validate_field_name(tokens[-1])) and tokens[1] in relational_operators)

def validate_select_clause(select_clause_tokens):
    
    # Only one '*' is allowed
    if select_clause_tokens == ['*']:
        return True
    
    # Comma must not be at either first or last position
    if select_clause_tokens[0] == ',' or select_clause_tokens[-1] == ',':
        return False
    
    # Commas must not be consecutive
    for tk_i, tk_j in list(zip(select_clause_tokens[:-1],select_clause_tokens[1:])):
        if tk_i == ',' and tk_j == ',':
            return False
        
    # Check if each alphanumeric string is a valid name
    for tk in select_clause_tokens:
        if tk == ',':
            continue
        else:
            if not validate_field_name(tk):
                return False
            
    # Two valid names must not be consecutive. It
    # indicates that there is a space in between
    for tk_i, tk_j in list(zip(select_clause_tokens[:-1],select_clause_tokens[1:])):
        if validate_field_name(tk_i) and validate_field_name(tk_j):
            return False
    
    return True

def validate_join_clause(join_clause_tokens):
    
    # A JOIN clause must have only one ON keyword
    # and it should be at index 1
    
    if join_clause_tokens[1] != 'ON' or join_clause_tokens.count("ON") != 1:
        return False
    
    return validate_table_name(join_clause_tokens[0]) and validate_relational_expression(join_clause_tokens[2:])

def validate_from_clause(from_clause_tokens):
    # There must be tokens after from keyword
    if from_clause_tokens == []:
        return False
    
    # Check if there is any JOIN keyword
    join_keyword_pos = len(from_clause_tokens)
    if "JOIN" in from_clause_tokens:
        join_keyword_pos = from_clause_tokens.index('JOIN')
        
        join_clause_tokens = from_clause_tokens[join_keyword_pos+1:]
    
        table_names = (from_clause_tokens[:join_keyword_pos-1] 
                        if from_clause_tokens[join_keyword_pos-1] in ['LEFT','RIGHT','INNER','FULL']
                        else from_clause_tokens[:join_keyword_pos])
        
        # Comma must not be at either first or last position
        if table_names[0] == ',' or table_names[-1] == ',':
            return False

        # Commas must not be consecutive
        for tk_i, tk_j in list(zip(table_names[:-1],table_names[1:])):
            if tk_i == ',' and tk_j == ',':
                return False

        # Check if each alphanumeric string is a valid name
        for tk in table_names:
            if tk == ',':
                continue
            else:
                if not validate_table_name(tk):
                    return False

        # Two valid names must not be consecutive. It
        # indicates that there is a space in between
        for tk_i, tk_j in list(zip(table_names[:-1],table_names[1:])):
            if validate_table_name(tk_i) and validate_table_name(tk_j):
                return False
        
        return validate_join_clause(join_clause_tokens)
    
    table_names = from_clause_tokens
    # Comma must not be at either first or last position
    if table_names[0] == ',' or table_names[-1] == ',':
        return False

    # Commas must not be consecutive
    for tk_i, tk_j in list(zip(table_names[:-1],table_names[1:])):
        if tk_i == ',' and tk_j == ',':
            return False

    # Check if each alphanumeric string is a valid name
    for tk in table_names:
        if tk == ',':
            continue
        else:
            if not validate_table_name(tk):
                return False

    # Two valid names must not be consecutive. It
    # indicates that there is a space in between
    for tk_i, tk_j in list(zip(table_names[:-1],table_names[1:])):
        if validate_table_name(tk_i) and validate_table_name(tk_j):
            return False
        
            
    return True

def validate_where_clause(where_clause_tokens):
    # The WHERE clause contains the condition
    
    # Case-I : The WHERE clause tokens' list is empty
    if where_clause_tokens == []:
        return False
    
    
    # Case-II : It must not start or end with a relational operator
    if where_clause_tokens[0] in relational_operators or where_clause_tokens[-1] in relational_operators:
        return False
    
    # Case-III : It must not start or end with a logical operator
    if where_clause_tokens[0] in ['AND','OR','NOT'] or where_clause_tokens[-1] in ['AND','OR','NOT']:
        return False
    
    # Case-IV : No relational operator must be consecutive, and no logical operator must be consecutive
    for tk_i, tk_j in list(zip(where_clause_tokens[:-1], where_clause_tokens[1:])):
        
        if tk_i in relational_operators and tk_j in relational_operators:
            return False
        
        if tk_i in ['AND','OR','NOT'] and tk_j in ['AND','OR','NOT']:
            return False
        
    # Logical Operators must separate relational expressions    
    
    relational_expressions = [[]]
    
    for tk in where_clause_tokens:
        if tk in ['AND','OR']:
            relational_expressions.append([])
        else:
            relational_expressions[-1].append(tk)
        
    validation_result = [validate_relational_expression(exp) for exp in relational_expressions]
    
    
    return reduce(lambda x, y: x and y, validation_result, True)

def tokenize_query(sql_query):
    sql_query_preprocessed = re.sub(r'^\s+|\s+$', '',                   sql_query)
    sql_query_preprocessed = re.sub(r',', ' , ',           sql_query_preprocessed)
    sql_query_preprocessed = re.sub(r'>',' > ',            sql_query_preprocessed)
    sql_query_preprocessed = re.sub(r'<',' < ',            sql_query_preprocessed)
    sql_query_preprocessed = re.sub(r'=',' = ',            sql_query_preprocessed)
    sql_query_preprocessed = re.sub(r'> = | >  = ',' >= ', sql_query_preprocessed)
    sql_query_preprocessed = re.sub(r'< = | <  = ',' <= ', sql_query_preprocessed)
    sql_query_preprocessed = re.sub(r'! = | !  = ',' != ', sql_query_preprocessed)
    
    tokens = re.split(r'\s+',sql_query_preprocessed)
    
    # If the token is a keyword, change it to uppercase
    tokens = list(map(lambda x: x.upper() if x.upper() in keywords else x,tokens))
    return tokens

__all__ = [
    'tokenize_query',
    'extract_from_clause',
    'extract_where_clause',
    'validate_select_clause', 
    'validate_from_clause', 
    'validate_where_clause'
]
