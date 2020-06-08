from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
from pymongo import MongoClient
import time
import os

#web_conection

def web_driver_initialize():

    #Firefox web driver initialization
    options = Options()
    options.headless = False
    driver = webdriver.Firefox(options=options, executable_path= (os.getcwd() + '/geckodriver'))

    return driver

def web_driver_close(web_driver):
    #close firefox web driver
    web_driver.close()
    
def login(web_driver):    

    #opening linkedin on web browser
    web_driver.get("https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin")

    #read email and password for login.csv file
    login_file = open("login.csv", "r").read()
    #Separate text read by line
    login_data = login_file.split("\n")

    #email in first line ande password in second line
    email = login_data[0]
    password = login_data[1]

    #fill in email and password and click on login button
    web_driver.find_element_by_name("session_key").send_keys(email)
    web_driver.find_element_by_name("session_password").send_keys(password)
    web_driver.find_element_by_class_name('login__form_action_container').click()

    time.sleep(10)

    if web_driver.title != "LinkedIn":
        raise Exception("Login Error")

    return web_driver

#input file read

def read_csv(file_name):

    #read input file with names to be searched
    file = open(file_name)
    content = str(file.read())

    #return a list of names to be searched
    return content.split("\n")

#web scraping

def go_scraping(web_driver, names, database):

    #scrapy each name in the name list
    for name in names:
        
        #do the search by modifying the url, adding keywords and replacing spaces with %20
        url = "https://www.linkedin.com/search/results/all/?keywords=" + name.replace(" ","%20") + "&origin=GLOBAL_SEARCH_HEADER"
        #open url in web browser
        web_driver.get(url)

        try:
            #click on first result
            web_driver.find_element_by_class_name('search-result__result-link').click()
            #wait page load
            time.sleep(5)

            #using bs4 to find the important information
            #create a BeautifulSoup object
            soup = BeautifulSoup(web_driver.page_source, 'html.parser')
        
            #find sections of interest
            experience = soup.find(id='experience-section')
            education = soup.find(id='education-section')
            certifications = soup.find(id='certifications-section')

            #certifiacations search
            certifications_list = []
            try:
                out_certifications = certifications.findAll(class_='pv-certifications__summary-info')
                for a in out_certifications:
                    certifications_list.append(a.find('h3').contents[0])
            except:
                #If have no certifications
                certifications_list.append("No certifications")

            #Education search
            education_list = []
            try:
                out_education = education.findAll(class_='pv-entity__degree-info')
                for a in out_education:
                    education_list.append(a.find('h3').contents[0])
            except:
                #If have no education
                education_list.append("No education")

            #Experience search
            experience_list = []
            try:
                out_experience = experience.findAll(class_='pv-entity__summary-info')
                for a in out_experience:
                    experience_data = {"Role": a.find('h3').contents[0],
                                       "Company": a.find(class_='pv-entity__secondary-title').contents[0].replace('\n', ""), 
                                       "Duration": a.find(class_='pv-entity__bullet-item-v2').contents[0]}
                    experience_list.append(experience_data)
            except:
                #If have no experience
                experience_list.append("No experience\n")

            #write output file

            user = {"Name": name, 
                    "Linkedin_Url": web_driver.current_url, 
                    "Certifications": certifications_list, 
                    "Education": education_list,
                    "Experience": experience_list}
            database.user.insert_one(user)


        except:
            #If the name is not found
            user = {"Name": name, "Linkedin_Url": "Not found", "Certifications": [], "Education": []}
            database.user.insert_one(user)


def connect_DB():
    
    client = MongoClient("mongodb+srv://mateus:d706b7@cluster-mg1vm.mongodb.net/linkedin_users?retryWrites=true&w=majority")
    database = client.linkedin_users

    return database

def main():
    
    try:
        db = connect_DB()
    except:
        print("DataBase connection Error")

    else:
        print("DataBase connection is OK")     
        try:
            driver = web_driver_initialize()        
        except:
            print("Web Driver Error")

        else:
            print("Web Driver is OK")
            try:
                login(driver)
            except:
                print("Login Error")
            
            else:
                print("Login is OK")
                
                try:
                    go_scraping(driver, read_csv("in.csv"), db)
                except:
                    print("Scraping Error")

                else:
                    print("Completed")
                    web_driver_close(driver)

if __name__ == "__main__":
    main()

