# users 

admin@example.com
- password 1 : placeholder 1

Floring@example.com
- password 2: placeholder 3


Useful Commands

## DB updates 
- Create Migration
> cd backend
> alembic revision --autogenerate -m "add task table"

- Apply migration :
> alembic upgrade head