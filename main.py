from query_validator import validate_query
from relational_algebra_generator import generate_relational_algebra

sql_query = input("Enter an SQL query : ")

if not validate_query(sql_query):
    print("The query is not valid.")
    exit(0)
    
relational_algebra = generate_relational_algebra(sql_query)

print(relational_algebra)
