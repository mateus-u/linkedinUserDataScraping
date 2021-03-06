from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time

#web_conection

def web_driver_initialize():

    #Firefox web driver initialization
    driver = webdriver.Firefox()
    #Minimize Firefox window
    driver.minimize_window()
    
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

    return web_driver

#input file read

def read_csv(file_name):

    #read input file with names to be searched
    file = open(file_name)
    content = str(file.read())

    #return a list of names to be searched
    return content.split("\n")

#web scraping

def go_scraping(web_driver, names):

    #clear the output file
    out = open("out.csv", "w")
    out.write("")
    out.close()
    
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
            time.sleep(3)

            #using bs4 to find the important information
            #create a BeautifulSoup object
            soup = BeautifulSoup(web_driver.page_source, 'html.parser')
        
            #output receives the string that will be written to the output file
            output = name + "," + web_driver.current_url 

            #find sections of interest
            experience = soup.find(id='experience-section')
            education = soup.find(id='education-section')
            certifications = soup.find(id='certifications-section')

            #certifiacations search
            output += '\nCertifications'
            try:
                out_certifications = certifications.findAll(class_='pv-certifications__summary-info')
                for a in out_certifications:
                    output += (',' + (a.find('h3').contents[0]))
            except:
                #If have no certifications
                output += ",No certifications"

            #Education search
            output += '\nEducation'
            try:
                out_education = education.findAll(class_='pv-entity__degree-info')
                for a in out_education:
                    output += (',' + (a.find('h3').contents[0]))
            except:
                #If have no education
                output += ",No education"

            #Experience search
            output += '\nExperience'
            try:
                out_experience = experience.findAll(class_='pv-entity__summary-info')
                for a in out_experience:
                    output += (',' + (str(a.find('h3').contents[0]) +','+str(a.find(class_='pv-entity__secondary-title').contents[0]).replace('\n', "") +','+ str(a.find(class_='pv-entity__bullet-item-v2').contents[0])) + '\n')
            except:
                #If have no experience
                output += ",No experience\n"

            #write output file
            out = open("out.csv", "a")
            out.write(output + '\n')

        except:
            #If the name is not found
            out = open("out.csv", "a")
            out.write(name + ',' "Nothing to say\n")



def main():
    
    driver = web_driver_initialize()
    login(driver)
    go_scraping(driver, read_csv("in.csv"))
    web_driver_close(driver)


if __name__ == "__main__":
    main()

