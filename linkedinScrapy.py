from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
import csv

#web_conection

def web_driver_initialize():
    driver = webdriver.Firefox()
    driver.minimize_window()
    return driver

def web_driver_close(web_driver):
    web_driver.close()
    
def login(web_driver):    

    web_driver.get("https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin")
    assert "LinkedIn Login, Sign in" in web_driver.title

    login_file = open("login.csv", "r").read()
    login_data = login_file.split("\n")

    email = login_data[0]
    password = login_data[1]

    web_driver.find_element_by_name("session_key").send_keys(email)
    web_driver.find_element_by_name("session_password").send_keys(password)
    web_driver.find_element_by_class_name('login__form_action_container').click()

    time.sleep(3)

    assert "LinkedIn" in web_driver.title

    return web_driver

#input file read

def read_csv(file_name):

    file = open(file_name)
    content = str(file.read())
    return content.split("\n")

#web scraping

def go_scraping(web_driver, names):

    out = open("out.csv", "w")
    out.write("")
    out.close()
    
    for name in names:
        
        url = "https://www.linkedin.com/search/results/all/?keywords=" + name.replace(" ","%20") + "&origin=GLOBAL_SEARCH_HEADER"
        web_driver.get(url)
        
        try:
            web_driver.find_element_by_class_name('search-result__result-link').click()
            time.sleep(3)
            ####################################################################
            soup = BeautifulSoup(web_driver.page_source, 'html.parser')
            
            output = name + "," + web_driver.current_url 

            experience = soup.find(id='experience-section')
            education = soup.find(id='education-section')
            certifications = soup.find(id='certifications-section')

            output += '\nCertifications'

            try:
                out_certifications = certifications.findAll(class_='pv-certifications__summary-info')

                for a in out_certifications:
                    output += (',' + (a.find('h3').contents[0]))

            except:
                output += ",No certifications"

            output += '\nEducation'
            try:

                out_education = education.findAll(class_='pv-entity__degree-info')

                for a in out_education:
                    output += (',' + (a.find('h3').contents[0]))

            except:
                output += ",No education"


            output += '\nExperience'

            try:
                out_experience = experience.findAll(class_='pv-entity__summary-info')

                for a in out_experience:
                    output += (',' + (str(a.find('h3').contents[0]) +','+str(a.find(class_='pv-entity__secondary-title').contents[0]).replace('\n', "") +','+ str(a.find(class_='pv-entity__bullet-item-v2').contents[0])) + '\n')
            
            except:
                output += ",No experience\n"

            ####################################################################
            out = open("out.csv", "a")
            out.write(output + '\n')
        except:
            out = open("out.csv", "a")
            out.write(name + ',' "Nothing to say\n")



def main():
    
    driver = web_driver_initialize()
    login(driver)
    go_scraping(driver, read_csv("in.csv"))
    web_driver_close(driver)


if __name__ == "__main__":
    main()

