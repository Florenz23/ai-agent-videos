from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException
import os
from pathlib import Path

def store_screenshot(html_path: str, output_path: str = None) -> bool:
    """
    Takes a screenshot of a local HTML file and saves it as a PNG.
    
    Args:
        html_path (str): Path to the HTML file to screenshot
        output_path (str, optional): Path where to save the screenshot. 
                                   If None, derives from html_path
    
    Returns:
        bool: True if successful, False otherwise
    
    Raises:
        ValueError: If html_path is invalid or empty
    """
    if not html_path:
        raise ValueError("HTML path cannot be empty")
        
    # If output_path not provided, create one based on html_path
    if output_path is None:
        output_dir = os.path.join('videos', 'webDev')
        output_path = os.path.join(output_dir, 'recent_screenshot.png')
    
    # Ensure output path ends with .png
    if not output_path.lower().endswith('.png'):
        output_path = os.path.splitext(output_path)[0] + '.png'
    
    try:
        # Convert relative path to absolute path
        absolute_path = os.path.abspath(html_path)
        if not os.path.exists(absolute_path):
            raise ValueError(f"HTML file not found: {absolute_path}")
            
        file_uri = Path(absolute_path).as_uri()
        
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Run in headless mode
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-gpu')  # Sometimes helps avoid issues
        
        # Initialize the driver
        driver = webdriver.Chrome(options=chrome_options)
        
        try:
            # Load the HTML file
            driver.get(file_uri)
            
            # Add a small delay to ensure page is fully loaded
            driver.implicitly_wait(2)
            
            # Ensure the output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Take screenshot
            driver.save_screenshot(output_path)
            print(f"Screenshot saved successfully at: {output_path}")
            return True
            
        finally:
            # Always close the driver
            driver.quit()
            
    except WebDriverException as e:
        print(f"WebDriver error: {str(e)}")
        return False
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False

def main():
    """Main function to demonstrate usage."""
    html_path = os.path.join("videos", "webDev", "recent_state.html")
    success = store_screenshot(html_path)
    if not success:
        print("Failed to create screenshot")

if __name__ == "__main__":
    main()