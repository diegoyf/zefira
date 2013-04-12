"""Zefira application v1.0 """

import tornado.httpserver
import tornado.web
import tornado.ioloop
import tornado.options
import os.path
import datetime
import pymongo
import uimodules

from tornado.options import define, options
from data_manag import DataManagement

define("port", default = 8000, help= "run on given port", type=int)

"""*************************************************************************
Application: Clase principal que inicializa los handlers e inicia la conexion 
con la base de datos. Ademas, asigna los modulosUI, los paths para los archivos
estaticos, templates, y otras settings de seguridad y cookies.

************************************************************************"""


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/publish", PublishHandler),
            (r"/login", LoginHandler),
            (r"/logout", LogoutHandler),
            (r"/box", BoxHandler),
            (r"/signup", SignUpHandler),
            (r"/clientes", ClientesHandler),
            (r"/empresas", EmpresasHandler),
            (r"/cbox", CBoxHandler),
            (r"/companies", CompaniesHandler),
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
            login_url = "/login",
            xsrf_cookies = True
        )
        
        self.dataManager = DataManagement()
        tornado.web.Application.__init__(self, handlers, **settings)


class BaseHandler(tornado.web.RequestHandler):
    @property
    def data_manager(self):
        return self.application.dataManager

    def get_current_user(self):

        user_id  = self.get_secure_cookie("username")
        password = self.get_secure_cookie("password")
        branch = self.get_secure_cookie("branch")
        
        user = self.application.dataManager.fetch_user(user_id, password, branch)
        if user:
            return user
        else:
            self.set_status(404)

class MainHandler(tornado.web.RequestHandler):
    
    def get(self):
        self.render(
            "index.html",
            page_title = "Zefira v-1.0 | Home",
            header_text = "Bienvenidos a Zefira",
            
            )
class PublishHandler(BaseHandler):
    @tornado.web.authenticated
    
    def get(self):
        
        self.render(
                "publish.html",
                page_title = " Zefira Publish Test",
                header_text = "Publica",
                message = True,
            )
    def post(self):

        import base64, uuid
        benefit = {
            "_id":"bene"+base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes),
            "title": self.get_argument("title"), 
            "description":self.get_argument("description"),
            "company_name": self.current_user['info']['name']
                  }
        self.data_manager.publish_benefit(benefit, self.current_user)
        self.redirect("/cbox")

class LoginHandler(BaseHandler):
    def get(self):
        self.render("login.html",
                    page_title ="Zefira | Login",
                    header_text= "Ingresa a Zefira",
                    
                    )
    def post(self):
        self.set_secure_cookie("username", self.get_argument("username"))
        self.set_secure_cookie("password", self.get_argument("password"))
        self.set_secure_cookie("branch", self.get_argument("branch"))
        if self.get_argument("branch") == "companies":
            self.redirect("/cbox")
        else:
            self.redirect("/box")

class LogoutHandler(BaseHandler):
    def get(self):
        if(self.get_argument("logout", None)):
            self.clear_cookie("zefira_user")
            self.redirect("/")
        self.redirect("/")

class ClientesHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(
            "clientes.html",
            page_title="Zefira | Clientes",
            header_text = "Zefira Clientes"
            )

class EmpresasHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(
            "empresas.html",
            page_title="Zefira | Empresas",
            header_text=" Zefira Empresas"
            )

class BoxHandler(BaseHandler):
    @tornado.web.authenticated
    
    def get(self): 
        interests = self.current_user['interests']    
        
        benefits = self.data_manager.fetch_benefits_usr(interests, self.current_user)
        
        self.render(
               "box.html",
               page_title = "Zefira | Inicio",
               header_text = "Box",
               user = self.current_user['username'],
               benefits = benefits,
               )

    def post(self):
        benefit_id  = self.get_argument("benefit_id")
        from bson.dbref import DBRef
        dbref_obj = DBRef('benefits', benefit_id)
        if dbref_obj in self.current_user['reserves']:
            for i in range(len(self.current_user['reserves'])):
                if self.current_user['reserves'][i] == dbref_obj:
                    del self.current_user['reserves'][i]
                    break
        else:
            self.current_user['reserves'].append(dbref_obj)
        self.db.users.save(self.current_user)
        self.redirect("/box")        
class CBoxHandler(BaseHandler):
    @tornado.web.authenticated

    def get(self):
        benefits_published = self.current_user['benefits']
        
        benefits_deref = self.data_manager.fetch_benefits_cmp(benefits_published)
        self.render(
            "cbox.html",
            page_title= "Zefira | Companies Box",
            header_text = "Companies Box",
            user = self.current_user['username'],
            benefits = benefits_deref
            )
        
class SignUpHandler(BaseHandler):
    
    def post(self):
        import base64, uuid
        

        if self.get_argument("branch") == "companies":
            
            new_user = {
                '_id':"comp"+base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes),
                'username': self.get_argument('username'),
                'password': self.get_argument('password'),
                'info' : {
                    'name': self.get_argument('name'),
                    'description': self.get_argument('description'),
                    'email' : self.get_argument('email')
                    },
                'benefits' : []
                }
            self.db.companies.save(new_user)
            self.set_secure_cookie("username", self.get_argument("username"))
            self.set_secure_cookie("password", self.get_argument("password"))
            self.set_secure_cookie("branch", self.get_argument("branch"))
            self.redirect("/cbox")
        
        else:
            user = {
                '_id':"user"+base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes),
                'username' : self.get_argument('username'),
                'password': self.get_argument('password'),
                'info':{'email': self.get_argument('email')},
                'interests': [],
                'reserves' : [],
                }
            self.db.users.save(user)
            self.set_secure_cookie("username", self.get_argument("username"))
            self.set_secure_cookie("password", self.get_argument("password"))
            self.set_secure_cookie("branch", self.get_argument("branch"))
            self.redirect("/box")

class CompaniesHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        companies = []
        for i in self.db.companies.find():
            companies.append(i)
        user_companies = self.current_user['interests']
        primary = []
        for i in user_companies:
            primary.append(self.db.dereference(i))
        for i in companies:
            if i in primary:
                i['message'] = "Siguiendo"
            else:
                i['message'] = "Seguir"
        
        self.render(
            "copres.html",
            page_title = "Zefira | Lista Empresas",
            header_text = "Empresas en Zefira",
            user = self.current_user['username'],
            companies = companies,
            )

    def post(self):
        company_id = self.get_argument("company_id")
        from bson.dbref import DBRef
        dbref_obj = DBRef('companies', company_id)
        if dbref_obj in self.current_user['interests']:
            for i in range(len(self.current_user['interests'])):
                if self.current_user['interests'][i] == dbref_obj:
                    del self.current_user['interests'][i]
                    break
        else:
            self.current_user['interests'].append(dbref_obj)
        self.db.users.save(self.current_user)
        self.redirect("/companies")
        

                 
def main():
    tornado.options.parse_command_line()
    server = tornado.httpserver.HTTPServer(Application())
    server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()




