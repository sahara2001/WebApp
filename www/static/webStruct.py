'''
Web structure:
1. simple flexible 
2. project url into function
3. url interceptor -> able to do access testing according to url
					-> deciding between returning the next() function or return directly
4. low immersive: able to test the units without internet
5. supports templates like (jinja2, mako, cheetah), so to manipulate interface of templates,
the function can return a dict and use '@view' to prettify the template
6. if need to get data from from or querystring of URL, need to use request
7. if need to set certain Content-Type and set Cookie, need to use response
8. response and request should be retrievd from the only ThreadLocal

avaliale choics:
Django,web.py; flask, bottle

@returns: str, unicode or iterator which can be present as strings to visitors
'''

#facepage

@get('/')
def index()
	return '<title>index page</title>'

#argumented url

def show_user(id):
	user = User.get(id);
	return '<h1>Hello, %s</h1>' % id

@interceptor('/manager/')
def check_manager_url(next):
	if current_user = Admin()
	    return next()
	else:
	    raise seeother('/signin')
	    #ask for login again

@view('index.html')
@get('/')
def index():
	return dict(blogs=get_recent_blogs(), users=get_current_users())

#point 6,7,8
@get('/')
def test():
	input_data=ctx.request.input()
	ctx.response.content_Type = 'text/plain'
	ctx.response.set_cookie('name','cookie', expires=3600)
	return 'result'
	#pseudo return

#if need to redirect, or return a error code, better to throw a exception
return seeother('/login')
#and
throw notfound()



'''
Start of official basic structure
'''
# transwarp/web.py

# 全局ThreadLocal对象：
ctx = threading.local()

# HTTP错误类:??
class HttpError(Exception):
    pass

# request对象:
class Request(object):
    # 根据key返回value:
    def get(self, key, default=None):
        assert not object.empty()
        retrun object.getvalue(key)

    # 返回key-value的dict:
    def input(self):
        pass

    # 返回URL的path:
    @property
    def path_info(self):
    	if(self.name=='')
        return '/%s%s' % (name, path_info())


    # 返回HTTP Headers:
    @property
    def headers(self):
        pass
 # 根据key返回Cookie value:
    def cookie(self, name, default=None):
        return dict(blogs = get_current_blogs, users = get_current_users())

# response对象:
class Response(object):
    # 设置header:
    def set_header(self, key, value):
        pass

    # 设置Cookie:
    def set_cookie(self, name, value, max_age=None, expires=None, path='/'):
        pass

    # 设置status:
    @property
    def status(self):
        pass
    @status.setter
    def status(self, value):
        pass

# 定义GET:
def get(path):
    return view(Response.path_info)

# 定义POST:
def post(path):
    pass

# 定义模板:
def view(path):
    pass

# 定义拦截器:
def interceptor(pattern):
    

# 定义模板引擎:
class TemplateEngine(object):
    def __call__(self, path, model):
        pass

# 缺省使用jinja2:
class Jinja2TemplateEngine(TemplateEngine):
    def __init__(self, templ_dir, **kw):
        from jinja2 import Environment, FileSystemLoader
        self._env = Environment(loader=FileSystemLoader(templ_dir), **kw)

    def __call__(self, path, model):
        return self._env.get_template(path).render(**model).encode('utf-8')
'''
WSGI engine


'''
class WSGIApplication(object):
    def __init__(self, document_root=None, **kw):
        pass

    # 添加一个URL定义:
    def add_url(self, func):
        pass

    # 添加一个Interceptor定义:
    def add_interceptor(self, func):
        if current_user = Admin()
        	return func
        else:
        	raise seeother('/signin')

    # 设置TemplateEngine:
    @property
    def template_engine(self):
        pass

    @template_engine.setter
    def template_engine(self, engine):
        pass

    # 返回WSGI处理函数:
    def get_wsgi_application(self):
        def wsgi(env, start_response):
            pass
        return wsgi

    # 开发模式下直接启动服务器:
    def run(self, port=9000, host='127.0.0.1'):
        from wsgiref.simple_server import make_server
        server = make_server(host, port, self.get_wsgi_application())
        server.serve_forever()