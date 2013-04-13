import pymongo

class DataManagement():
    
    def __init__(self):
        
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
            else:
                user = self.db.companies.find_one({"username":username})
                
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
        wrong = ""
        if branch == 'bene':
            
            benefits = []
            for i in self.db.benefits.find():
                benefits.append(i)
            if len(benefits) == 0: return True

            for i in benefits:
                if data['company_name'] == i['company_name'] and data['title'] == i['title']:
                    wrong = False
                    return wrong
            if wrong == False:
                pass
            else:
                return True
        elif branch == "comp":
            
            companies = []
            for i in self.db.companies.find():
                companies.append(i)
                for i in companies:
                    if data['username'] == i['username']:
                        return wrong
            return True
        else:
            
            users = []
            for i in self.db.users.find():
                users.append(i)

            for i in users:
                if data['username'] == i['username']:
                    return wrong
            return True


    def fetch_benefits_cmp(self,benefits_ref):
        benefits_deref = []
        if not benefits_ref:
            return None
        for i in range(len(benefits_ref)):
            benefits_deref.append(self.db.dereference(benefits_ref[i]))
        return benefits_deref
    
    def create_user(new_user, branch):
        pass

    def fetch_companies_cbox(user_companies):
        pass

    def follow_fnc_company(company_id):
        pass
    
    def reserve_fnc_users(benefit_id):
        pass
    
    
    
    
    
    
    
