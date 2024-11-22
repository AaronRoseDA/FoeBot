from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By  # Import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import codecs
import re
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
import numpy as np
from dotenv import load_dotenv
import os
from PIL import Image
import math 
import random
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.chrome.options import Options
import cv2
import shutil


# Specify the path to your .env file
env_path = r"C:\Users\arose\OneDrive - Ortho Molecular Products\Desktop\side projects\FoE app\.env"
load_dotenv(dotenv_path=env_path)

# Retrieve variables
USRNAME = os.getenv("USRNAME")
USRPWD = os.getenv("USRPWD")


def launch_game(username, password, window_size=(1920, 1200), window_position=(-2560, 100)):
    """
    Automates the login process and selects the world in the game.
    
    Args:
        driver: Selenium WebDriver instance.
        username: Username for login.
        password: Password for login.
        window_position (tuple): Tuple (x, y) to set the window position on the screen.
        window_size (tuple): Tuple (width, height) to set the window size.
    """
    try:
        # Launch webdriver and load website
        options = webdriver.ChromeOptions()
        options.add_argument(f"--window-size={window_size[0]},{window_size[1]}")
        options.add_argument(f"--window-position={window_position[0]},{window_position[1]}")
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option(
            "prefs",
            {
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False,
                "profile.default_content_setting_values.notifications": 2
                # with 2 should disable notifications
            },
            )
        driver = webdriver.Chrome(service=webdriver.chrome.service.Service(ChromeDriverManager().install()), options=options)
        
        driver.get('https://us13.forgeofempires.com/game/index?ref=master-page-login')
        
        
        
        # Set window position and size
        driver.set_window_position(*window_position)
        driver.set_window_size(*window_size)
        
        # Wait for the username input field and enter username
        usr_name = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "page_login_always-visible_input_player-identifier"))
        )
        usr_name.send_keys(username)
    
        # Wait for the password input field and enter password
        usr_pwd = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "page_login_always-visible_input_password"))
        )
        usr_pwd.send_keys(password)
    
        # Wait for the login button and click it
        lgn_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "page_login_always-visible_button_login"))
        )
        lgn_btn.click()
        time.sleep(1)
    
        # Wait for the Play button and click it
        play_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "play_now_button"))
        )
        play_btn.click()
        time.sleep(1)
    
        # Wait for the Noarsil button and click it
        noarsil_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[@class='world_select_button' and @value='us13']"))
        )
        noarsil_btn.click()

        time.sleep(5)
        # Calculate the center position, 100 pixels down from the top
        center_x = driver.execute_script("return window.innerWidth") // 2        
        # Execute a click at the calculated coordinates
        action = ActionBuilder(driver)
        action.pointer_action.move_to_location(center_x, 200)
        action.pointer_action.click()
        action.perform()
        return(driver)
    except Exception as e:
        print(f"Error: {e}")
 
def get_template_paths(search_attribute):
    base_path = r"C:\Users\arose\OneDrive - Ortho Molecular Products\Desktop\side projects\FoE app\assets"
    attribute_paths = {
        "zoom": os.path.join(base_path, "zoom.png"),
        "coins": os.path.join(base_path, "coins"),
        "troops": os.path.join(base_path, "troops"),
        "collectProduction": os.path.join(base_path, "productionReady"),
        "idleBuildings": os.path.join(base_path, "idleBuilding"),
        "trainTroops": os.path.join(base_path, "trainTroops"),
        "makeProduction": os.path.join(base_path, "produce"),
        "crates": os.path.join(base_path, "crates"),
        "forgeBar": os.path.join(base_path, "progression", "forgePoints"),
        "researchMenu": os.path.join(base_path, "progression", "researchMenu"),
        "progressBar": os.path.join(base_path, "progression", "progressBar"),
        "spendPoints": os.path.join(base_path, "progression", "spendPointsButton"),
        "unlockTech": os.path.join(base_path, "progression", "unlockNowButton"),
        "returnToCity": os.path.join(base_path, "progression", "returnButton"),
        "clearPopup": os.path.join(base_path, "clearPopup", "xOut.png"),
        "missionCheckMark": os.path.join(base_path, "missionComplete", "greenCheck.png"),
        "collectMissionReward": os.path.join(base_path, "missionComplete", "collectReward.png"),
        "townHall": os.path.join(base_path, "townHall", "townHall.png"),
    }

    template_path = attribute_paths.get(search_attribute)
    if not template_path:
        return None

    # If the path is for a single file
    if template_path.endswith(".png"):
        return [template_path]

    # If the path is a directory, gather all image files within it
    template_paths = [
        os.path.join(template_path, filename)
        for filename in os.listdir(template_path)
        if filename.lower().endswith(('.png', '.jpg', '.jpeg'))
    ]
    return template_paths        

get_template_paths("clearPopup")

def take_screenshot(driver, fail_safe = True):
    
    if fail_safe:
        clear_map(driver)
        time.sleep(max(0, random.gauss(.3, 0.05)))
    # takes a screenshot and writes it to the drive  
    screenshot_dir = r"C:\Users\arose\OneDrive - Ortho Molecular Products\Desktop\side projects\FoE app\ScreenShots"
    os.makedirs(screenshot_dir, exist_ok=True)
    timestamp = int(time.time() * 1000)
    screenshot_path = os.path.join(screenshot_dir, f"screenshot_{timestamp}.png")
    driver.save_screenshot(screenshot_path) 
    return(screenshot_path)       


def clear_map(driver):
    center_x = driver.execute_script("return window.innerWidth") // 2  
    action = ActionBuilder(driver)
    action.pointer_action.move_to_location(center_x, 4)
    action.pointer_action.click()
    action.perform()
   
def element_location(driver, search_attribute = "zoom", shift_amount = 0, threshold = .8, fail_safe = True): 
    # finds the x, y location of a provided serach attribute
    # returns a list of x, y points    
    
    def find_asset(screenshot_path, template_path):
        img_rgb = cv2.imread(screenshot_path)
        template = cv2.imread(template_path)        

        res = cv2.matchTemplate(img_rgb, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= threshold)
        
        return loc, img_rgb, template
    
    def draw_rect_asset(loc, img_rgb, template):
        h, w = template.shape[:-1]
        for pt in loc:  # Switch columns and rows
            #print(w, h)
            cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
        cv2.imwrite(r"C:\Users\arose\OneDrive - Ortho Molecular Products\Desktop\side projects\FoE app\assets\result.png", img_rgb)
    

    template_paths = get_template_paths(search_attribute)

    screenshot_path = take_screenshot(driver, fail_safe)
    
    loc_clean = []            
    for template in template_paths:
        #print(template)
        loc_out, img_rgb, template = find_asset(screenshot_path, template)
        loc_out = list(zip(loc_out[1], loc_out[0]))
        loc_clean.append(loc_out)

    loc_clean = [pt for sublist in loc_clean for pt in sublist]
    
    draw_rect_asset(loc_clean, img_rgb, template)
    
    for pt in loc_clean:
        for pt_comp in loc_clean:  # Iterate over a copy to avoid modifying during iteration
            distance = math.sqrt((pt_comp[0] - pt[0])**2 + (pt_comp[1] - pt[1])**2)        
            if distance < 5 and distance != 0:
                if pt_comp in loc_clean:  # Check if pt_comp is still in the list
                    loc_clean.remove(pt_comp)
                    
    loc_clean = [(x + shift_amount, y + shift_amount) for x, y in loc_clean]
        
    return(driver, loc_clean)

def interact_with_site (driver, loc = 0, mode = "click", vertical = 0, horizontal = 0, clicks = 1, fail_safe = False):
    # Function for interaction with site. Given x y 
    if mode == "click": 
        for x, y in loc:
            for i in range(0, clicks):
                action = ActionBuilder(driver)
                action.pointer_action.move_to_location(x, y)
                action.pointer_action.click()
                action.perform()  
                time.sleep(max(0, random.gauss(.3, 0.05)))
                
                if fail_safe:
                    time.sleep(max(0, random.gauss(.3, 0.05)))
                    clear_map(driver)
                
                print("point clicked...")

    
    if mode == "pan":      
        element = driver.find_element(By.ID, "game_body")
        action = ActionChains(driver)
        action.click_and_hold(element).move_by_offset(horizontal, vertical).release().perform() 

def clear_popup(driver):
    driver, xOut_location = element_location(driver, "clearPopup", 5, fail_safe = True)
    interact_with_site(driver, loc = xOut_location, mode="click", clicks=1, fail_safe=True)
    print("popup cleared")

def zoom_change(driver):
    driver, zoom_location = element_location(driver, "zoom", 5, fail_safe = True)
    interact_with_site(driver, loc = zoom_location, mode="click", clicks=1, fail_safe=True)

def collect_coins(driver):
    driver, coin_locations = element_location(driver, "coins", 10, fail_safe = True)
    interact_with_site(driver, loc = coin_locations, mode="click", clicks=1, fail_safe=True)

def collect_crates(driver):
    driver, crate_locations = element_location(driver, "crates", 5)
    interact_with_site(driver, loc = crate_locations, mode="click", clicks=1, fail_safe=True)
    
def collect_production(driver):
    driver, production_locations = element_location(driver, "collectProduction", 5)
    interact_with_site(driver, loc = production_locations, mode="click", clicks=1, fail_safe=True)

def collect_troops(driver):
    driver, troop_locations = element_location(driver, "troops", 5, threshold=.5)
    interact_with_site(driver, loc = troop_locations, mode="click", clicks=1, fail_safe=True)

def order_troops (driver, fail_safe = False):   

    driver, idle_locations = element_location(driver, "idleBuildings", 5, threshold=.5)
      
    for point in idle_locations: 
        #point = idle_locations[0]
        print([point])
        interact_with_site(driver, loc = [point], mode="click", clicks=1, fail_safe=False)
        time.sleep(max(0, random.gauss(.5, 0.1)))
        driver, train_button_locations = element_location(driver, "trainTroops", 5, threshold=.8, fail_safe=False)
        if train_button_locations:
            interact_with_site(driver, loc = [train_button_locations[0]], mode="click", clicks=1, fail_safe=False)
            time.sleep(max(0, random.gauss(.5, 0.1)))     
            clear_map(driver)        
            print("troop trained")
        clear_map(driver) 

def order_production (driver, fail_safe = False):  

    driver, idle_locations = element_location(driver, "idleBuildings", 5, threshold=.5)
           
    for point in idle_locations: 
        #point = idle_locations[0]
        #print([point])
        interact_with_site(driver, loc = [point], mode="click", clicks=1, fail_safe=False)
        time.sleep(max(0, random.gauss(.5, 0.1)))
        driver, production_button_locations = element_location(driver, "makeProduction", 5, threshold=.8, fail_safe=False)
        if production_button_locations:
            interact_with_site(driver, loc = [production_button_locations[0]], mode="click", clicks=1, fail_safe=False)
            time.sleep(max(0, random.gauss(.5, 0.1)))     
            clear_map(driver)        
            print("production ordered")
        clear_map(driver) 

def collect_rewards (driver, fail_safe = False): 

    driver, green_check_locations = element_location(driver, "missionCheckMark", 15, threshold=.5)
        
    for point in green_check_locations: 
        #point = idle_locations[0]
        print([point])
        interact_with_site(driver, loc = [point], mode="click", clicks=1, fail_safe=False)
        time.sleep(max(0, random.gauss(.5, 0.1)))
        driver, collect_reward_locations = element_location(driver, "collectMissionReward", 5, threshold=.8, fail_safe=False)
        if collect_reward_locations:
            interact_with_site(driver, loc = [collect_reward_locations[0]], mode="click", clicks=1, fail_safe=False)
            time.sleep(max(0, random.gauss(.5, 0.1)))     
            clear_map(driver)        
            print("mission reward collected")
        clear_map(driver) 
       
def clear_screenshots_folder(path):
    """
    Deletes all files and subdirectories in the provided folder.

    Parameters:
    path (str): Path to the folder to clear.
    """
    if not os.path.exists(path):
        print(f"The folder '{path}' does not exist.")
        return

    # Iterate through each item in the folder
    for item in os.listdir(path):
        item_path = os.path.join(path, item)

        try:
            # Check if it's a file or directory
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)  # Remove file or symbolic link
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)  # Remove directory and its contents
        except Exception as e:
            print(f"Error while deleting {item_path}: {e}")

    print(f"All data in the folder '{path}' has been deleted.")


#%%
#clear popup
clear_popup(driver)
collect_coins(driver)
collect_production(driver)
collect_crates(driver)
collect_troops(driver)
order_production(driver)
order_troops(driver)
clear_screenshots_folder(r"C:\Users\arose\OneDrive - Ortho Molecular Products\Desktop\side projects\FoE app\ScreenShots")

#%%

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
driver = launch_game(USRNAME, USRPWD)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

total_duration = 14400  # 1 hour
start_time = time.time()

# Define the folder path for clearing screenshots
screenshot_folder = r"C:\Users\arose\OneDrive - Ortho Molecular Products\Desktop\side projects\FoE app\ScreenShots"

# Main loop
while (time.time() - start_time) < total_duration:
    try:
        # Execute the defined functions
        clear_map(driver)
        clear_popup(driver)
        collect_coins(driver)
        collect_production(driver)
        collect_crates(driver)
        collect_troops(driver)
        order_production(driver)
        order_troops(driver)
        clear_screenshots_folder(screenshot_folder)

        print(f"Tasks completed- {time.strftime('%H:%M.%S')}. Waiting for the next interval...")
    except Exception as e:
        print(f"An error occurred during task execution: {e}")

    # Randomized delay between 6 and 8 minutes
    delay = random.uniform(300, 360)
    print(f"Sleeping for {int(delay / 60)} minutes and {int(delay % 60)} seconds.")
    time.sleep(delay)

print("Execution completed.")

driver.close()




















































