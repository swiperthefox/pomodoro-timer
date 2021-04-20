"""A simple Model class that support basic SQL operations (on sqlite3).

A subclass Entity of Model maps to a table in the database.

The `_table` attribute specifies the database table name. Default is the lower case of class name.

The `_fields` attribute defines the field names and their types of the table, in form of Dict[name, type].

The subclass could define default values for the fields, as class variables. If no default value for a 
field is provided, the default value of its type will be used.

Method defined in Model class:

* __init__(self, *kw): a keyword based constructor, which just initialize the fields with the given values.
* cls.query_db(**where): return a list of entities that satisfies the criteria stated in the `where` parameters.
* cls.query_db_fields(field_names, **where): similar as `query_db`, return a list sqlite3.Row objects.
* save_to_db(fields=[]): insert or update the entity. 
    If the entity is not saved before, the `fields` parameter is ignored.
    Otherwise, only update the fields listed in `fields` parameter.
* cls.create(*args, **kw): create an instance by passing all arguments to the constructor, then save to database by
calling the save_to_db method.
method which will insert or update an instance of the subclass to the corresponding table.
"""
import db

class WrongFieldNameError(NameError):
    def __init__(self, field, table):
        msg = f'"{field}" is not valid field name in table "{table}"'
        super().__init__(msg)

class WrongFieldValueError(ValueError): pass

def maybe_apply(f, v):
    return None if v is None else f(v)
    
class Model:
    _fields = {}
    _table_name = ""
    _saved_to_db = False
    
    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        if not cls._table_name:
            cls._table_name = cls.__name__.lower()
        for k, t in cls._fields.items():
            if k not in cls.__dict__:
                setattr(cls, k, t())
        
        # add type annotations, so that dataclass can recognize the fields too.
        anno = '__annotations__'
        if not hasattr(cls, anno):
            setattr(cls, anno, {})
        annotations = getattr(cls, anno)
        for k, t in cls._fields.items():
            if k not in annotations:
                annotations[k] = t
        # the type of `id` field is int, it starts with None value which is intercepted as 'null'
        # by sqlite3, and a new id will be generated for it.
        cls._fields['id'] = int
        if getattr(cls, 'id', 0) > 0:
            raise WrongFieldValueError(f'"id" field is reserved for row id, it must be 0 before it get the real row id from database.')
        setattr(cls, 'id', None)
    
    def __init__(self, **field_values):
        for name, value in field_values.items():
            if name not in self._fields:
                raise WrongFieldNameError(name, self._table_name)
            setattr(self, name, value)
            
    @classmethod
    def create(cls, *args, **kw):
        new_entity = cls(*args, **kw)
        new_entity.save_to_db()
        return new_entity
        
    @classmethod
    def query_db(cls, **where):
        sql, params = cls._build_query_sql(cls._fields, **where)   
        data_list =  db.execute_query(sql, params)
        entities = [cls(**data) for data in data_list]
        for e in entities:
            e._saved_to_db = True
        return entities
    
    @classmethod
    def query_db_fields(cls, fields, **where):
        sql, params = cls._build_query_sql(fields, **where)
        return db.execute_query(sql, params)
        
    def save_to_db(self, fields = []):
        # verify field names
        if fields == []: 
            fields = list(self._fields.keys())
        else:
            for k in fields:
                if k not in self._fields:
                    raise WrongFieldNameError(k, self._table_name)
        
        
        # should not change the 'id' field
        fields = [name for name in fields if name != 'id']
        
        sql = self._update_to_db_sql(fields) if self._saved_to_db else self._insert_to_db_sql(fields) 
        parameters = tuple(maybe_apply(self._fields[k], getattr(self, k)) for k in fields)
        
        lastrowid = db.execute_commit(sql, parameters)
        if not self._saved_to_db:
            self.id = lastrowid
            self._saved_to_db = True
    
    def _update_to_db_sql(self, fields):
        set_clause = ', '.join(field + " = ?" for field in fields) # "name=?, age=?"
        sql = f'''UPDATE {self._table_name}
            SET {set_clause}
            WHERE id = {self.id}
        '''
        return sql
        
    def _insert_to_db_sql(self, fields):
        sql = f'''INSERT INTO {self._table_name}
            ({', '.join(fields)})
            VALUES ({','.join("?"*len(fields))})
        '''
        return sql
        
    @classmethod
    def _build_query_sql(cls, fields=['*'], **where):
        criterial = []
        parameters = []
        for k, v in where.items():
            if k not in cls._fields:
                print(f'{cls._fields=}')
                raise WrongFieldNameError(k, cls._table_name)
            else:
                criterial.append(f'{k} = ?')
                parameters.append(maybe_apply(cls._fields[k], v))
        if criterial:
            where_clause = " WHERE " + " and ".join(criterial)
        else:
            where_clause = ""
            
        if fields != ['*']:
            for f in fields:
                if f not in cls._fields:
                    raise WrongFieldNameError(f, cls._table_name)
        sql = f'SELECT {", ".join(fields)} FROM {cls._table_name}{where_clause}'
        return sql, parameters
        