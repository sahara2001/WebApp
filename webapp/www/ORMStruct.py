'''
ORM structure:
1.Mysql structure
@methods:
@visiting sql:establishing link, set cursur object, run sql syntax, catch and deal with exceptions

INSERT():inert user data
SELECT(): search data
UPDATE():
DELETE():

2. User model
'''
'''
LInk pool
establishing link pool
@feature:  every http link can get a direct link to the database
@stored by __pool, is losing data, use 'utf-8 coding set'
'''

@asyncio.coroutine
def creating_pool(loop, **kw):
	logging.info('create database connection pool ...')
	global __pool
		__pool yield from aiomysql.create_pool(
		host = kw.get('host','localhost')
		port = kw.get('port', '3306')
		user = kw.get('user')
		password = kw.get('password')
		db=kw['db']
		charset=kw.get('charset')
		autocommit=kw.get('autocommit')
		maxsize=kw.get('maxsize')
		minsize=kw.get('minsize')
		loop=loop
		)
'''
SQL语句的占位符是?，而MySQL的占位符是%s，select()函数在内部自动替换。注意要始终坚持使用带参数的SQL，而不是自己拼接SQL字符串，这样可以防止SQL注入攻击。

注意到yield from将调用一个子协程（也就是在一个协程中调用另一个协程）并直接获得子协程的返回结果
'''
#select
@asyncio.coroutime
def select(sql, args, size = None):
	log(sql, args)
	global __pool
	with (yield from __pool) as conn
		cur = yield from conn.cursor(aiomysql.DictCursor)
		yield from cur.execute(sql.replace ('?', '%') , (args or None))
		if size:
			rs = yield from cur.fetchmany(size);
		else
			rs = yield from cur.fetchall();
		#return all if no size argument
		logging.info('rows returned: %s rows', size)
		return rs

#if the following three instruction requires same arguments, try to use a new execute command to replace
#execute

@aiomysql.coroutine
def execute(sql, args):
    log(sql)
    global __pool 		# not included in source
    with (yield from __pool) as conn:
	try:
            cur = yield from conn.cursor()
	    yield from cur.execute(sql.replace ('?', '%') , args)
            affected = cur.rowcount
	    yield from cur.close()
	except BaseException as e:
	    raise
	return affected
	
	
#findAll
#findNumber
#update
#delete

'''
USER MODEL: 
@struct: name, id
'''
# from orm import Model, StringField, IntegerField

'''
设计ORM需要从上层调用者角度来设计。

我们先考虑如何定义一个User对象，然后把数据库表users和它关联起来。
'''

#class User(Model):
#	__table__ = 'users'
#
#	id = IntegerField(primary_key = True)
#	name = StringField()

'''
# 创建实例:
user = User(id=123, name='Michael')
# 存入数据库:
user.insert()
# 查询所有User对象:
users = User.findAll()
'''

'''
先定义所有ORM映射的基类Model
'''

class Model(dict, metaclass=ModelMetaclass):		# inherit from dict
    def __init__(self, **kw):
	super(Model, self).__init__(**kw)		# use base model to direct initialize attributes
	
    def __getattr__(self, key):
	try:
	    return self[key]
	except KeyError:
	    raise AttributeError(r"'Model' object has no attribute '%s'" % key)
    def __setattr__(self, key, value):
	self[key] = value

    def getValue(self, key):
	return getattr(self, key, None)
    
    def getValueOrDefault(self, key):
	value = getattr(self, key, None)		#why third argument -> None is default return
	if value is None:
	    field = self. __mapping__[key]		#why use mapping not direct call
	    if field.default is not None:
	        value = field.default() if callable(field.default) else field.default
		logging.debug('using default value for %s: %s' % (key, str(value)))
		setattr(self, key, value)
	return value

    @classmethod
    @asyncio.coroutine
    def find(cls, pk):
        ' find object by primary key'
	rs = yield from select('%s where `%s`=?' % (cls.__select__, cls.__primary_key__), [pk], 1)
	if len(rs) == 0:
	    return None
	return cls(**rs[0])

    @classmethod
    @asyncio.coroutine
    def save(self):
        args = list(map(self.getValueOrDefault, self.__fields__))
        args.append(self.getValueOrDefault(self.__primary_key__))
        rows = yield from execute(self.__insert__, args)
        if rows != 1:
            logging.warn('failed to insert record: affected rows: %s' % rows)
	    
	    
    @classmethod
    async def findAll(cls, where=None, args=None, **kw):
        ' find objects by where clause. '
        sql = [cls.__select__]
        if where:
            sql.append('where')
            sql.append(where)
        if args is None:
            args = []
        orderBy = kw.get('orderBy', None)
        if orderBy:
            sql.append('order by')
            sql.append(orderBy)
        limit = kw.get('limit', None)
        if limit is not None:
            sql.append('limit')
            if isinstance(limit, int):
                sql.append('?')
                args.append(limit)
            elif isinstance(limit, tuple) and len(limit) == 2:
                sql.append('?, ?')
                args.extend(limit)
            else:
                raise ValueError('Invalid limit value: %s' % str(limit))
        rs = await select(' '.join(sql), args)
        return [cls(**r) for r in rs]

    @classmethod
    async def findNumber(cls, selectField, where=None, args=None):
        ' find number by select and where. '
        sql = ['select %s _num_ from `%s`' % (selectField, cls.__table__)]
        if where:
            sql.append('where')
            sql.append(where)
        rs = await select(' '.join(sql), args, 1)
        if len(rs) == 0:
            return None
        return rs[0]['_num_']

    
    @asyncio.coroutine
    def update()
	args = list(map(self.getValue, self.__fields__))
        args.append(self.getValue(self.__primary_key__))
        rows = await execute(self.__update__, args)
        if rows != 1:
            logging.warn('failed to update by primary key: affected rows: %s' % rows)

	
    @asyncio.coroutine
    def remove(self)		#??? what to remove ???
    	args = [self.__primary_key__]
        affected = await execute(self.__delete__, args)			#use await instead of yield from (in source code -> await)
	if affected != 1:						#only one user allowed to exist
	    logging.warn('failed to delete record: no rows affected)
	
 
'''
>>>user['id']
123
>>>user.id
123
'''

class Field(object):				# base model used to project into database?
    def __init__(self, name, column_type, primary_key, default):
	self.name = name
	self.column_type = column_type
	self.primary_key = primary_key
	self.default = default
	
    def __str__(self):
	return '<%s, %s:%s>' % (self.__class__.__name__, self.column_type, self.name)

class StringField(Field):
	
    def __init__(self, name = None, primary_key = False, default = None)
	super().__init__(name, ddl, primary_key, default)

'''
注意到Model只是一个基类，如何将具体的子类如User的映射信息读取出来呢？答案就是通过metaclass：ModelMetaclass：
''''
	
class ModelMetaclass(type):
    def __new__(cls, name, bases, attrs):
	# exempt from Model class itself
	if name == 'Model':
	    return type.__new__(cls, name, bases, attrs)
        # get the name of table:
	tableName = attrs.get('__table__', None) or name    #not boolean 
	logging.info('found model: %s (table: %s)' % (name, tableName))
	#get all the fieldname and main key name:
	mappings = dict()
	fields = []
	primaryKey = None
	for k, v in attrs.items();
	   if isinstance(v, Field):
		logging.info('  found mapping: %s ==> %s' % (k, v))
		mappings[k] = v
		if v.primaryKey:
			#find primary key
		    if primaryKey:
		        raise RuntimeError('Duplicate primary key for field: %' % k)
		
		    primaryKey = k
	        else:
		    fields.append(k)
	if not primaryKey:
	    raise runtimeError('Primary key not found.')
        for k in mappings.keys():
	    attrs.pop(k)
	escaped_fields = list(map(lambda f: '`%s`' % f, fields))
	attrs['__mappings__'] = mappings  # save the relationship between attributes and column
	attrs['__table__'] = tableName
	attrs['__primary_key__'] = primaryKey  # name of main key
	attrs['__fields__'] = fields # name except primary key
	#construct default SELECT, INSERT, UPDATE and DELETE
	attrs['__select__'] = 'select `%s` (%s, `%s`) values (%s)' %(tableName, ','.join(escaped_fields), tableName)
	attrs['__insert__'] = 'insert into `%s` (%s, `%s`) value (%s)' % (tableName, ','.join(escaped_fields), primaryKey, create_args_string(len(escaped_field) + 1))
	attrs['__delete__'] = 'delete from `%s` where `%s`=?' % (tableName, primaryKey)
	attrs['__update__'] = 'update `%s` SET %s WHERE `%s`=?' % (tableName, ','.join(map(lambda f: '`%s`=?' % (mappings.get(f).name or f), fields)), primaryKey)
	
	return type.__new__(cls, name, bases, attrs)

'''
这样，任何继承自Model的类（比如User），会自动通过ModelMetaclass扫描映射关系，并存储到自身的类属性如__table__、__mappings__中。

然后，我们往Model类添加class方法，就可以让所有子类调用class方法：
'''
'''
class Model(dict):
    
    ...
    
    @classmethod
    @asyncio.coroutine
    def find(cls, pk):
        ' find object by primary key'
	rs = yield from select('%s where `%s`=?' % (cls.__select__, cls.__primary_key__), [pk], 1)
	if len(rs) == 0:
	    return None
	return cls(**rs[0])
	

   
	
'''
User类现在就可以通过类方法实现主键查找：
user = yield from User.find('123')

往Model类添加实例方法，就可以让所有子类调用实例方法：
'''
class Model(dict):

    ...

    @asyncio.coroutine
    def save(self):
        args = list(map(self.getValueOrDefault, self.__fields__))
        args.append(self.getValueOrDefault(self.__primary_key__))
        rows = yield from execute(self.__insert__, args)
        if rows != 1:
            logging.warn('failed to insert record: affected rows: %s' % rows)
	    
	    
    @classmethod
    async def findAll(cls, where=None, args=None, **kw):
        ' find objects by where clause. '
        sql = [cls.__select__]
        if where:
            sql.append('where')
            sql.append(where)
        if args is None:
            args = []
        orderBy = kw.get('orderBy', None)
        if orderBy:
            sql.append('order by')
            sql.append(orderBy)
        limit = kw.get('limit', None)
        if limit is not None:
            sql.append('limit')
            if isinstance(limit, int):
                sql.append('?')
                args.append(limit)
            elif isinstance(limit, tuple) and len(limit) == 2:
                sql.append('?, ?')
                args.extend(limit)
            else:
                raise ValueError('Invalid limit value: %s' % str(limit))
        rs = await select(' '.join(sql), args)
        return [cls(**r) for r in rs]

    @classmethod
    async def findNumber(cls, selectField, where=None, args=None):
        ' find number by select and where. '
        sql = ['select %s _num_ from `%s`' % (selectField, cls.__table__)]
        if where:
            sql.append('where')
            sql.append(where)
        rs = await select(' '.join(sql), args, 1)
        if len(rs) == 0:
            return None
        return rs[0]['_num_']

    
    @asyncio.coroutine
    def update()
	args = list(map(self.getValue, self.__fields__))
        args.append(self.getValue(self.__primary_key__))
        rows = await execute(self.__update__, args)
        if rows != 1:
            logging.warn('failed to update by primary key: affected rows: %s' % rows)

	
    @asyncio.coroutine
    def remove(self)		#??? what to remove ???
    	args = [self.__primary_key__]
        affected = await execute(self.__delete__, args)			#use await instead of yield from (in source code -> await)
	if affected != 1:						#only one user allowed to exist
	    logging.warn('failed to delete record: no rows affected)
	
    
    
'''
	
		
'''
最后一步是完善ORM，对于查找，我们可以实现以下方法：

findAll() - 根据WHERE条件查找；

findNumber() - 根据WHERE条件查找，但返回的是整数，适用于select count(*)类型的SQL。

以及update()和remove()方法。

所有这些方法都必须用@asyncio.coroutine装饰，变成一个协程。

调用时需要特别注意：

user.save()
没有任何效果，因为调用save()仅仅是创建了一个协程，并没有执行它。一定要用：

yield from user.save()
才真正执行了INSERT操作。
'''
	
