
# Import the required packages
import bs4 #  BeautifulSoup - Web Scraping
from selenium import webdriver # Selenium - Web Automation
from selenium.webdriver.common.keys import Keys # Keys - Keyboard Keys
from webdriver_manager.chrome import ChromeDriverManager # Chrome Driver Manager
import time # Time - Time Delay
from selenium.webdriver.common.by import By # By - Find Element
from selenium.webdriver.common.action_chains import ActionChains # Action Chains - Mouse Hover
from bs4 import BeautifulSoup as bs # BeautifulSoup - Web Scraping
from pprint import pprint # Pretty Print - Print in a better format
import pandas as pd # Pandas - Data Manipulation

# %%
# driver = webdriver.Chrome(ChromeDriverManager().install())

# %%
# Create a class to simulate a web browser 
# This class will be used to log into Linkedin 
class WebSimulator: 
    # Initialize the class
    def __init___(self): 
        # Create a variable to store the webdriver
        self.driver = None

    # Create a function to log into Linkedin   
    def log_into_linkedin(self, user_name, password):
        
        print("Attempting to log into Linkedin")
        # try:
            # Create a webdriver
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        # self.driver = webdriver.Chrome(executable_path=r"chromedriver")
            # Get the Linkedin login page
        self.driver.get("https://www.linkedin.com")
        # Find the username field and enter the username 
        user = None
        while user is None:
            try:
                user = self.driver.find_element(By.ID, 'session_key')
            except:
                # refresh the page
                self.driver.refresh()
        
        user.send_keys(user_name)
        # Find the password field and enter the password
        pass_element = self.driver.find_element(By.ID, 'session_password')
        pass_element.send_keys(password)
        # Find the login button and click it
        log_in_button = self.driver.find_element(By.XPATH, "//button[@data-id='sign-in-form__submit-btn']")
        log_in_button.click()
        # Print a success message
        print("Successfully logged into Linkedin :)")
        # If the login is unsuccessful   
        # except:
        #     print("Login unsuccessful :(")
        
    # Create a function to scrape the data    
    def load_scrape_page(self, celeb):
        try:
            # Get the Linkedin page of the celebrity
            self.driver.get("https://www.linkedin.com/in/"+celeb+"/recent-activity/shares/")
        except:
            # Print an error message
            print("Could not access page :(")


# %%
# Create a class to scrape the data
class LinkedinScraper:
    def __init__(self, driver):
        # Initialize the class and create a dictionary to store the data
        self.columns = {'Posted date':None,
                        'Post text':None,
                        'Is it reposted?':None,
                        'Post likes':None, 
                        'Post comments':None, 
                        'Post reposts':None, 
                        'Post Article Link':None
                       }
        # Create a variable to store the webdriver
        self.driver = driver
        # Create a variable to store the dataframe
        self.dataframe = None
        # Create a variable to store the post list
        self.post_list = None
        # Create a variable to store the excel name
        self.excel_name = None
    
    # Create a function to scrape the data
    def create_dataframes(self):
        # initializes dataframe to push to excel
        self.dataframe = pd.DataFrame(columns = list(self.columns.keys()))
        
    # Create a function to scrape the data   
    def set_post_list(self):
        # gets the page source
        company_page = self.driver.page_source
        # parses page source into soup format
        linkedin_soup = bs(company_page.encode("utf-8"), "html")
        # filters post info and returns a list
        self.post_list = linkedin_soup.findAll("div",{"class":"feed-shared-update-v2"})
        
    # Create a function to scrape the data of copy for the post   
    def get_post_text(self,  container, row_map):
        # attempts to get post text with one of 2 approaches depending on where text is
        
        try:
            # gets the text container
            text_cont = container.find("div",{"class":"update-components-text"})
            # gets the text
            text_tag = text_cont.findChild('span').findChild('span')
            # checks if the text is in a different format
            if(text_tag.has_attr('dir')):
                row_map['Post text'] = text_tag.get_text().strip()
            else:
                text_tag = text_cont.findChild('span')
                row_map['Post text'] = text_tag.get_text().strip()
        except:
            pass
        
     # Create a function to scrape the date of the post   
    def get_posted_date(self,  container, row_map):
        try:
            # gets the date container
            date_cont = container.find("div").find("div",{"class":"update-components-actor"}).find("a")["aria-label"]
            # gets the date
            posted_date_iter = date_cont.split('.')[-1].strip().split()
            if(posted_date_iter[-2]=='Edited'):
                row_map['Posted date'] = posted_date_iter[-4]
            else:
                row_map['Posted date'] = posted_date_iter[-2]
        except:
            pass
        
    # Create a function to check if the post is reposted and how many times    
    def get_if_reposted(self,  container, row_map):
        try:
            cont = container.find("div").find("div",{"class":"update-components-header"}).find("div",{"class":"update-components-header__text-wrapper"}).find("span",{"class":"update-components-header__text-view"}).find("div",{"class":"update-components-text-view"}).find('span').find('span')
            reposted_text = cont.get_text().strip()
            row_map['Is it reposted?']  = reposted_text.split()[0].capitalize()
        except:
            row_map['Is it reposted?']  = 'Original'
            
     # Create a function to check if the post has any urls     
    def get_post_article_link(self,  container, row_map):
        try:
            row_map['Post Article Link'] = container.find("div").find("article",{"class":"update-components-article"}).find("div",{"class":"update-components-article--with-large-image"}).find("div",{"class":"update-components-article__link-container"}).find("a")['href']
        except:
            try:
                row_map['Post Article Link'] = container.find("div").find("div",{"class":"update-components-mini-update-v2"}).find("div",{"class":"update-components-actor"}).find("a")['href']
            except:
                pass
                
    # Create a function to check the number of likes
    def get_post_likes(self, container, row_map):
        try:
            socialItems = container.find("div",{"class":"social-details-social-activity"})
            row_map['Post likes'] = socialItems.find("span",{"class":"social-details-social-counts__reactions-count"}).get_text()
        except:
            pass

    # Create a function to check the number of comments and reposts   
    def get_post_comments_and_reposts(self, container, row_map):
        try:
            socialItems = container.findAll("li",{"class":"social-details-social-counts__item"})
            for item in socialItems:
                item_text = item.get_text().strip()
                if 'comment' in item_text:
                    row_map['Post comments'] = item_text.strip().split()[0]
                if 'repost' in item_text:
                    row_map['Post reposts'] = item_text.strip().split()[0]
        except:
            pass
    
    # Create a function to scrape the data of copy for the post
    def populate_single_post_info(self, container):

        # creates a dictionary to store the data
        row_map  = self.columns.copy()

        # populates the dictionary
        self.get_post_text(container, row_map)
        self.get_posted_date(container, row_map)
        self.get_if_reposted(container, row_map)
        self.get_post_article_link(container, row_map)
        self.get_post_likes(container, row_map)
        self.get_post_comments_and_reposts(container, row_map)
        
        # returns the dictionary
        return row_map
    
    # Populate the dataframe with the data for all posts
    def populate_dataframe(self):
        for post in self.post_list:
            post_info = self.populate_single_post_info(post)
            self.dataframe = pd.concat([self.dataframe, pd.DataFrame([post_info])], ignore_index=True)
            
    # Write the dataframe to an excel file
    def write_to_excel(self):
        with pd.ExcelWriter(self.excel_name) as writer:
            self.dataframe.to_excel(writer, sheet_name='sheet1')
        
    # Create a function to create the excel file with the data for all posts
    def posts_to_excel(self, file_name):
        
        try:
        # Initialize dataframes and set post data
            self.excel_name = file_name
            self.create_dataframes()
            self.set_post_list()

            # parse post data and fit to excel
            self.populate_dataframe()
            self.write_to_excel()

            # print success message
            print("File "+file_name+" with",len(self.post_list),"posts info created.")
            
        except:
            print("Error: Could not create file.")
        
        # deallocate class variables 
        self.dataframe = None
        self.post_list = None
        self.excel_name = None

        
        


# %%
# Enter the username of the public profile to scrape

import streamlit as st

st.title("Linkedin Scraper")

PERSON_TO_SCRAPE = st.text_input("Enter the username of the public profile to scrape")
#PERSON_TO_SCRAPE = "amitsevak"
start_time = time.time()
time_spent = 0
text_box = st.text("Input the username and wait for 10 seconds to load the page")
while time_spent < 10:
    time_spent = time.time() - start_time
    text_box.text("Input the username and wait for {} seconds to load the page".format(10 - int(time_spent)))
    time.sleep(1)

st.write("Wait for login to complete")

# %%
# Run the class with the username and password of the account used to access the public profile
USERNAME = "johnydoey7531@gmail.com"
PASSWORD = "JohnyDoeyProtect1357!"

chrome_session = WebSimulator()
chrome_session.log_into_linkedin(USERNAME,PASSWORD)

st.write("Login complete")
st.write("Scroll through the page to load all posts")
chrome_session.load_scrape_page(PERSON_TO_SCRAPE)

# wait for 30 seconds to load all posts
start_time = time.time()
time_spent = 0
text_box = st.text("Scroll through the page to load all posts")
while time_spent < 30:
    time_spent = time.time() - start_time
    text_box.text("Scroll through the page to load all posts for {} seconds".format(30 - int(time_spent)))
    time.sleep(1)

# %%
# Run the class to scrape the data and create the excel file

scraper = LinkedinScraper(chrome_session.driver)
import datetime
filename = PERSON_TO_SCRAPE + "_post_info" + datetime.datetime.now().strftime("%Y%m%d") + ".xlsx"
scraper.posts_to_excel(filename)
with open(filename, 'rb') as f:
    bytes = f.read()
    st.download_button(label='Download file', data=bytes, file_name=filename, mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

time.sleep(20)
st.stop()
