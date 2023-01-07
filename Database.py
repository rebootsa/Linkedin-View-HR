from pymongo import MongoClient
import time, random, os, csv, platform
import logging
from datetime import datetime
log = logging.getLogger(__name__)
def setupLogger() -> None:
    dt: str = datetime.strftime(datetime.now(), "%m_%d_%y %H_%M_%S ")
    if not os.path.isdir('./logs'):
        os.mkdir('./logs')
    # TODO need to check if there is a log dir available or not
    logging.basicConfig(filename=('./logs/' + str(dt) + 'Database.log'), filemode='w',
                        format='%(asctime)s::%(name)s::%(levelname)s::%(message)s', datefmt='./logs/%d-%b-%y %H:%M:%S')
    log.setLevel(logging.DEBUG)
    c_handler = logging.StreamHandler()
    c_handler.setLevel(logging.DEBUG)
    c_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%H:%M:%S')
    c_handler.setFormatter(c_format)
    log.addHandler(c_handler)
DataList = ['Users','People','Company','URL','HR']
class Data:
    def __init__(self) -> None:
        self.username = ""
        self.password = ''
        self.Connected_DB = MongoClient(f"mongodb+srv://{self.username}:{self.password}@cluster0.z58rf.mongodb.net/?retryWrites=true&w=majority")
        self.Database = self.Connected_DB["Linked"]
        setupLogger()
    def SetCookies(self,Post,username):
        Set_BD = Post
        self.Database[DataList[0]].insert_one({"username":username,"cookies":Set_BD})
    def GetCookies(self,username):
        DB = self.Database[DataList[0]]
        get_User = DB.find_one({"username":username},{'_id': False})
        if get_User != None:
            log.info("I'm Found For User >> "+username)
            return get_User['cookies']
        else:
            log.info("I'm Not Found For User >> "+username)
            return False
    def GetCompany(self):
        DB = self.Database[DataList[2]]
        get_Company = DB.find({},{'_id': False})
        return get_Company
    def SetCompany(self,Post):
        Set_BD = Post
        self.Database[DataList[2]].insert_one(Post)
    def GetUrl_link(self,num):
        DB = self.Database[DataList[3]]
        return DB.find_one({"num":num},{"_id":False})
    def SetUrl_link(self,Post):
        Set_BD = Post
        self.Database[DataList[3]].insert_one(Post)
    def DelCookies(self,Post,username):
        Set_BD = Post
        self.Database[DataList[0]].delete_one({"username":username,"cookies":Set_BD})
    def Set_HR_profile(self,Post):
        Set_BD = Post
        self.Database[DataList[4]].insert_one(Post)