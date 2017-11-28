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
		if size == None:
			rs = yield from cur.fetchmany(size);
		else
			rs = yield from cur.fetchall();
		#return all if no size argument
		logging.info('rows returned: %s rows', size)
		return rs


#insert

@aiomysql.coroutine
def insert(sql, args, contant, size = None):
	log(sql, args)
	global __pool
	rs = select(sql, args, constant, size)
	if size = None:
		return
	else:
		re.execute(sql.replace('?', 'args') % (constant or None))
		return


#Update

#Delete
def delete(sql,args,size = None):
	log(sql,args)
	global __pool
	re yield from select(sql, args, size)
	re.execute(sql.delete())
	return

'''
USER MODEL: 
@struct: name, id
'''
from orm import Model, StringField, IntegerField

class User(Model):
	self.name = 'users'

	id = IntegerField(primary_key = True)
	name = StringField

