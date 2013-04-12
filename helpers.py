import pymongo

conn = pymongo.Connection("localhost",27017)
db = conn.zefira

def validation(d):
    branch = d['_id'][:4]
    wrong = ""
    if branch == 'bene':
        print "bene branch"
        
        benefits = []
        
        for i in db.benefits.find():
            benefits.append(i)
        if len(benefits) == 0: return True

        for i in benefits:
            if d['company_name'] == i['company_name'] and d['title'] == i['title']:
                wrong = False
                return wrong
        if wrong == False:
            pass
        else:
            return True
    elif branch == "comp":
        print "comp branch"
        
        companies = []
        for i in db.companies.find():
            companies.append(i)
        for i in companies:
            if d['username'] == i['username']:
                return wrong
        return True

    else:
        print "users branch"
        
        users = []
        for i in db.users.find():
            users.append(i)

        for i in users:
            if d['username'] == i['username']:
                return wrong
        return True


                
    
        
