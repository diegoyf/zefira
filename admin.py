import tornado.httpserver
import tornado.web
import tornado.ioloop
import tornado.options
import os.path
import uimodules

from tornado.options import define, options
from data_manag import DataManagement


define("port", default=8000, help="run on given port", type = int)

class Admin(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/clientes", ClientesHandler),
            (r"/empresas", EmpresasHandler),
            (r"/abox", AdminBoxHandler)
            ]
        settings = dict(
            template_path = os.path.join(os.path.dirname(__file__), "templates"),
            static_path = os.path.join(os.path.dirname(__file__),"static"),
            ui_modules={
                "Benefit" : uimodules.BenefitModule,
                "BenefitCo": uimodules.BenefitCoModule,
                "Company" : uimodules.CompaniesModule},            
            debug = True,
            cookie_secret = "0azgrztWSuenSRWevq9GAOp/4bDtSET0q8YII0ZfLDc=",
            login_url = "/",
            xsrf_cookies = True
        )
        self.dataManager = DataManagement("zefira")
        tornado.web.Application.__init__(self, handlers, **settings)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(
            "admin_main.html",
            page_title = "Zefira | Admin Site"
            )
    def post(self):
        self.set_secure_cookie("username", self.get_argument("username"))
        self.set_secure_cookie("password", self.get_argument("password"))
        self.redirect("/abox")

class BaseHandler(tornado.web.RequestHandler):
    @property
    def data_manager(self):
        return self.application.dataManager
    
    def get_current_user(self):
        user_id = self.get_secure_cookie("username")
        password = self.get_secure_cookie("password")
        branch = "admin"
        user = self.application.dataManager.fetch_user(user_id, password, branch)
        return user

class AdminBoxHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.write("You're in Admin Box: " + self.current_user['username'])

class ClientesHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        pass

class EmpresasHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        pass



def main():
    tornado.options.parse_command_line()
    server = tornado.httpserver.HTTPServer(Admin())
    server.listen(8080)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()

