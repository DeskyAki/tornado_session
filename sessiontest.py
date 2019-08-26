import tornado.web
from session import Session
import tornado.ioloop


class BaseHandler(tornado.web.RequestHandler):
    # 钩子函数, 子类初始化时候会将子类对象传入该方法中执行
    def initialize(self):
        # 这里将子类对象传入session中, 则以后生成的session对象中就包含处理器的实例对象
        self.session = Session(self)


class IndexHandler(BaseHandler):
    def get(self):
        self.render("a.html")

    def post(self, *args, **kwargs):
        if self.get_argument('name', None) == '123':
            self.session['is_login'] = True
            self.session['name'] = self.get_argument('name')
            self.redirect('/admin')
        else:
            self.write('登录失败, 请重新登录!')


class AdminHandler(BaseHandler):
    def get(self):
        if self.session['is_login']:
            self.write('欢迎%s回来. ' % (self.session['name'],))
        else:
            self.redirect('/index')


settings = {
    "cookie_secret": 'test-secret,',
    'template_path': 'template',
}

application = tornado.web.Application([
    (r"/index", IndexHandler),
    (r"/admin", AdminHandler),
], **settings)


if __name__ == '__main__':
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
利用利用
