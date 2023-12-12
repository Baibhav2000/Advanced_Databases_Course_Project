from utils import (
                rel_alg_operators,
                tokenize_query,
                extract_where_clause,
                extract_from_clause
            )
import re
from itertools import permutations

def generate_relational_algebra(sql_query):
    
    sql_tokens = tokenize_query(sql_query)
    
    where_keyword_pos = len(sql_tokens)
    where_clause_tokens = []
    
    if "WHERE" in sql_tokens:
        where_keyword_pos = sql_tokens.index("WHERE")
        where_clause_tokens.extend(extract_where_clause(sql_tokens, where_keyword_pos))
    
    from_keyword_pos = sql_tokens.index("FROM")
    
    from_clause_tokens = extract_from_clause(sql_tokens, from_keyword_pos, where_keyword_pos)
    
    table_names = []
    
    join_clause_tokens = []
    join_keyword_pos = len(from_clause_tokens)
    
    if "JOIN" in from_clause_tokens:
        join_keyword_pos = from_clause_tokens.index("JOIN")
        join_clause_tokens = from_clause_tokens[join_keyword_pos+1:]

        table_names = (from_clause_tokens[:join_keyword_pos-1]
                       if from_clause_tokens[join_keyword_pos-1] in ['LEFT', 'RIGHT', 'INNER', 'FULL']
                       else from_clause_tokens[:join_keyword_pos])
    else:
        table_names = from_clause_tokens
        
    select_clause_tokens = sql_tokens[1:from_keyword_pos]
    
    relational_algebra = ""
    
    if join_clause_tokens != []:
        if from_clause_tokens[join_keyword_pos-1] in ['LEFT','RIGHT','INNER','FULL']:
            relational_algebra = f"{table_names[0]}{rel_alg_operators[from_clause_tokens[join_keyword_pos-1]]}({''.join(join_clause_tokens[-3:])}){join_clause_tokens[0]}"
        else:
            relational_algebra = f"{table_names[0]}{rel_alg_operators['JOIN']}({''.join(join_clause_tokens[-3:])}){join_clause_tokens[0]}"
    else:
        relational_algebra = ' \u00d7 '.join([token for token in from_clause_tokens if token != ','])
    
    if where_clause_tokens != []:
        
        where_condition = ""
        
        for token in where_clause_tokens:
            if token in ['AND', 'OR']:
                where_condition += rel_alg_operators[token]
            else:
                where_condition += token
        
        relational_algebra = f"{rel_alg_operators['WHERE']}({where_condition})({relational_algebra})"
    
    if select_clause_tokens != ['*']:
        relational_algebra = f"{rel_alg_operators['SELECT']}({''.join(select_clause_tokens)})({relational_algebra})"
    
    return relational_algebra

def generate_equivalent_expressions(relational_algebra):
    exp_list = [relational_algebra]
    
    # Cascading of σ operator 
    for exp in exp_list:
        match = re.search(r'σ\((.*⋀.+.*)\)\((\w+)\)', exp)
        
        if match:
            conditions = match.group(1).split('⋀')
            
            conditions = [f'σ({cond})' for cond in conditions]
            
            new_exp = match.group(2)
            for cond in conditions[::-1]:
                new_exp = cond + f"({new_exp})"

            new_exp = exp.replace(match.group(0), new_exp)
            
            exp_list.append(new_exp)
    
    # Commutative property of ⨝ operator
    for exp in exp_list:
        match = re.search(r'([A-Za-z_]+)([⨝⟕⟖⟗]\(.*\))([A-Za-z_]+)',exp)
        
        if match:
            perms = list(permutations([match.group(1), match.group(3)]))
            
            for perm in perms:
                new_exp = match.group(2).join(perm)
                new_exp = exp.replace(match.group(0),new_exp)
                
                exp_list += [new_exp] if new_exp not in exp_list else []
    
    # Commutative property of × operator
    for exp in exp_list:
        match = re.search(r'([A-Za-z_]+) × ([A-Za-z_]+) (× ([A-Za-z_]+))*',exp)
        if match:
            table_names = match.group(0).split(' × ')
            perms = list(permutations(table_names))
            
            for perm in perms:
                new_exp = ' × '.join(perm)
                new_exp = exp.replace(match.group(0),new_exp)
                
                exp_list += [new_exp] if new_exp not in exp_list else []
                
    return exp_list

__all__ = [
    'generate_relational_algebra',
    'generate_equivalent_expressions'
]
