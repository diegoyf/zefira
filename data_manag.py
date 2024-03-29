import pymongo

class DataManagement():
    
    def __init__(self,database):
        
        if database == "zefira":
            conn = pymongo.Connection("localhost", 27017)
            self.db = conn.zefira
    
    def fetch_benefits_usr(self,interests_ref, user):
        companies_followd = []
        benefits_dref = []
        benefits = []

        if len(interests_ref) == 0: 
            return None
        else:

            for i in interests_ref:
                companies_followd.append(self.db.dereference(i))
            for j in range(len(companies_followd)):
                for i in range(len(companies_followd[j]['benefits'])):
                    benefits_dref.append(companies_followd[j]['benefits'][i])
            for i in benefits_dref:
                benefits.append(self.db.dereference(i))
            
            reserves = user['reserves']
            if len(reserves) == 0 :
                for i in benefits:
                    i['message'] = "Reservar" 
            else:
                reserves_dref = []
                for i in range(len(reserves)):
                    reserves_dref.append(self.db.dereference(reserves[i]))

                for i in benefits:
                    if i in reserves_dref:
                        i['message'] = "Reservado"
                    else:
                        i['message'] = "Reservar"
            return benefits

    def fetch_user(self,username,password,branch):
        try:
            if branch == "clientes":
                user = self.db.users.find_one({'username':username})
            elif branch == "companies":
                user = self.db.companies.find_one({"username":username})
            else: 
                user = self.db.admin.find_one({'username': username})
            
            if user['password'] == password:
                return user
            else:
                raise Exception
        except:
            return None

    def publish_benefit(self,benefit,user):

        from bson.dbref import DBRef
        if self.validate(benefit):
            self.db.benefits.save(benefit)
            user['benefits'].append(DBRef('benefits', benefit["_id"]))
            self.db.companies.save(user)
        else: 
            raise Exception #Really lame fix
        

    def validate(self,data):
        branch = data['_id'][:4]
        
        if branch == 'bene':
            
            benefits = []
            for i in self.db.benefits.find():
                benefits.append(i)
            if len(benefits) == 0: return True
            for i in benefits:
                if data['company_name'] == i['company_name'] and data['title'] == i['title']:
                    return False
            return True
        elif branch == "comp":
            
            companies = []
            for i in self.db.companies.find():
                companies.append(i)
                for i in companies:
                    if data['username'] == i['username']:
                        return False
            return True
        else:
            
            users = []
            for i in self.db.users.find():
                users.append(i)
            for i in users:
                if data['username'] == i['username']:
                    return False
            return True

    def fetch_benefits_cmp(self,benefits_ref):
        
        benefits_deref = []
        if not benefits_ref:
            return None
        for i in range(len(benefits_ref)):
            benefits_deref.append(self.db.dereference(benefits_ref[i]))
        return benefits_deref
    
    def create_user(self, new_user, branch):
        if branch == "companies" and self.validate(new_user):
            self.db.companies.save(new_user)
            return "/cbox"
        elif branch == "clientes" and self.validate(new_user):
            self.db.users.save(new_user)
            return "/box"
        else:
            return "/error"
    def fetch_companies(self, user_companies):
        companies = []
        for i in self.db.companies.find():
            companies.append(i)
        primary = []
        for i in user_companies:
            primary.append(self.db.dereference(i))
        for i in companies:
            if i in primary:
                i['message'] = "Siguiendo"
            else:
                i['message'] = "Seguir"
        return companies
    
    def follow_fnc_company(self, company_id, current_user):
        from bson.dbref import DBRef
        
        dbref_obj = DBRef('companies', company_id)
        if dbref_obj in current_user['interests']:
            for i in range(len(current_user['interests'])):
                if current_user['interests'][i] == dbref_obj:
                    del current_user['interests'][i]
                    break
        else:
            current_user['interests'].append(dbref_obj)
        self.db.users.save(current_user)
    
    def reserve_fnc_users(self, benefit_id, current_user):
        from bson.dbref import DBRef
        
        dbref_obj = DBRef('benefits', benefit_id)
        if dbref_obj in current_user['reserves']:
            for i in range(len(current_user['reserves'])):
                if current_user['reserves'][i] == dbref_obj:
                    del current_user['reserves'][i]
                    break
        else:
            current_user['reserves'].append(dbref_obj)
        self.db.users.save(current_user)
    
    def delete_edit_user(self,user_id, branch, delete = True):
        pass
    def delete_edit_benefit(self, benefit_id, delete = True):
        pass   
    def delete_create_reference(collection, reference , create = True):
        pass
    
    
    
    
