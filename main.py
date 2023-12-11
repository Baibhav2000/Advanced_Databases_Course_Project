from query_validator import validate_query
from relational_algebra_generator import generate_relational_algebra, generate_equivalent_expressions

sql_query = input("Enter an SQL query : ")

if not validate_query(sql_query):
    print("The query is not valid.")
    exit(0)
    
relational_algebra = generate_relational_algebra(sql_query)

equivalent_expressions = generate_equivalent_expressions(relational_algebra)

print("\nEquivalent expression(s) for the given query is/are:\n")
for exp in equivalent_expressions:
    print(exp)
    
print()
