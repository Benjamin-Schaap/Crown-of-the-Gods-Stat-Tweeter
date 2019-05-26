from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
import time
import shelve
import logging

# Initialize the logging object for testing.
logging.basicConfig(level=logging.CRITICAL, format=' %(asctime)s - %(levelname)s %(message)s')


""" 
    Function will return 'False' if there are no credentials and 'True if there are. Currently

    Currently, if a credential didn't exist, the try statement will never execute due to an error
    being throw. Thus the return 'False' statements will never execute.
"""
def CheckCredentials():

    checkShelve = shelve.open('loginData')

    try:
        # Check COTG credentials
        if checkShelve['cotgUsername'] is None or checkShelve['cotgPassword'] is None:
            logging.critical('No COTG credentials')
            return False

        # Check Twitter credentials
        elif checkShelve['twitterUsername'] is None or checkShelve['twitterPassword'] is None:
            logging.critical('No Twitter credentials')
            return False
        else:
            return True
    # TODO: I'm sure there is a better/simpler way to check for empty keys in the shelve object. Make code cleaner.
    except:
        logging.critical('Credentials are nonexistent or incomplete')
        return False


# Function prompts the user for credentials to COTG and Twitter. Stores them in a Shelve object
def GetCredentials():

    # Gets usernames and passwords from the user
    username = input('Enter your COTG email\n')
    password = input('Enter your COTG password\n')

    loginShelve = shelve.open('loginData')
    loginShelve['cotgUsername'] = username
    loginShelve['cotgPassword'] = password

    # Gets username and password from the user
    username = input('Enter your email used for twitter\n')
    password = input('Enter your twitter password\n')

    loginShelve['twitterUsername'] = username
    loginShelve['twitterPassword'] = password

# Function reads the COTG website, logs into the account provided by the user, and reads stats
# The stats read are: Denari, Wood, Stone, Iron, Food, Rank, and Score.
def ReadCotgStats():

    browser = webdriver.Chrome(executable_path='/Users/benja/Downloads/chromedriver')
    browser.get('https://www.crownofthegods.com/')

    objectOfInterest: WebElement
    tweet = ''# 'tweet' holds the cotg stats to be tweeted later


    try: # to click the login button
        objectOfInterest = browser.find_element_by_id('alreadregistlogin')
        objectOfInterest.click()
    except:
        logging.critical('Was not able to click the login button')

    try: # to login
        loginShelve = shelve.open('loginData')

        objectOfInterest = browser.find_element_by_id('email')
        objectOfInterest.send_keys(loginShelve['cotgUsername'])
        objectOfInterest = browser.find_element_by_id('passwrd')
        objectOfInterest.send_keys(loginShelve['cotgPassword'])
        objectOfInterest = browser.find_element_by_id('nilgin')
        objectOfInterest.click()
    except:
        logging.critical('Was not able to enter login credentials')

    try: # to read denari balance and login to the most recent world
        time.sleep(2)
        objectOfInterest = browser.find_element_by_id('denbalance')

        tweet += 'Your Denari balance is: ' + objectOfInterest.text + '\n'
        logging.debug(tweet)
        tweet += '\n' #formatting

        objectOfInterest = browser.find_element_by_id('selwrld')
        objectOfInterest.click()
    except:
        logging.debug('Was not able to login to world')

    try: # to read resources
        time.sleep(5)
        objectOfInterest = browser.find_element_by_id('totalWood')
        logging.debug('Your wood balance is: ' + objectOfInterest.text)
        tweet += 'Your wood balance is: ' + objectOfInterest.text + '\n'

        objectOfInterest = browser.find_element_by_id('totalStone')
        logging.debug('Your stone balance is: ' + objectOfInterest.text)
        tweet += 'Your stone balance is: ' + objectOfInterest.text + '\n'

        objectOfInterest = browser.find_element_by_id('totalIron')
        logging.debug('Your iron balance is: ' + objectOfInterest.text)
        tweet += 'Your iron balance is: ' + objectOfInterest.text + '\n'

        objectOfInterest = browser.find_element_by_id('totalFood')
        tweet += 'Your food balance is: ' + objectOfInterest.text + '\n'
        logging.debug('Your food balance is: ' + objectOfInterest.text + '\n')

    except:
        logging.critical('Was not able to read resources')

    try: # to read ranking and score

        time.sleep(4)
        objectOfInterest = browser.find_element_by_id('rankicontb')
        objectOfInterest.click()
        objectOfInterest.click()

        objectOfInterest = browser.find_element_by_id('playerRank')
        tweet += '\n' + 'Your rank is: ' + objectOfInterest.text + '\n'
        logging.debug('Your rank is: ' + objectOfInterest.text)

        objectOfInterest = browser.find_element_by_id('plstSco')
        tweet += 'Your score is: ' + objectOfInterest.text
        logging.debug('Your score is: ' + objectOfInterest.text)
    except:
        logging.critical('Was not able to read player stats')

    browser.close()
    return tweet

# Function logs into the Twitter account provided by the user and tweets the stats read from the COTG website
def PostToTwitter(tweet):

    browser = webdriver.Chrome(executable_path='/Users/benja/Downloads/chromedriver')
    browser.get('https://twitter.com/')

    objectOfInterest: WebElement

    try: # to lick on the 'login' button
        objectOfInterest = browser.find_element_by_link_text('Log in')
        objectOfInterest.click()
    except:
        logging.critical('Was not able to click the login button')

    try: # to log in to Twitter
        loginShelve = shelve.open('loginData')

        time.sleep(2)
        objectOfInterest = browser.find_element_by_class_name('js-username-field')
        objectOfInterest.send_keys(loginShelve['twitterUsername'])

        objectOfInterest = browser.find_element_by_class_name('js-password-field')
        objectOfInterest.send_keys(loginShelve['twitterPassword'])

        browser.find_element_by_class_name('EdgeButtom--medium').click()
    except:
        logging.critical('Was not able to log in')

    try: # to Tweet the stats
        time.sleep(2)
        objectOfInterest = browser.find_element_by_id('tweet-box-home-timeline')
        objectOfInterest.click()

        objectOfInterest.send_keys(tweet)
        browser.find_element_by_css_selector('button.tweet-action').click()
    except:
        logging.critical('Was not able to send Tweet')

    browser.close()

# Function that runs the script
if __name__ == '__main__':

    # If credentials exist, run the rest of the script. Otherwise get credentials from user and then run the script
    if CheckCredentials():
        tweet = ReadCotgStats()
        PostToTwitter(tweet)
    else:
        GetCredentials()
        tweet = ReadCotgStats()
        PostToTwitter(tweet)
