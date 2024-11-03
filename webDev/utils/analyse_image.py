import base64
from openai import OpenAI
from typing import Optional
import os

def analyse_start_image(image_path: str) -> str:
    try:
        # Initialize OpenAI client
        client = OpenAI()
        
        # Function to encode the image
        def encode_image(image_path: str) -> str:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        
        # Encode the image
        base64_image = encode_image(image_path)
        
        # Default prompt if none provided

        default_prompt = """
        You are tasked with providing a highly detailed description of a website based on an image. 
        This description will be used to recreate the website, so it's crucial to be as thorough 
        and accurate as possible. Follow these instructions carefully:

        1. Initial Analysis:
        - Examine the image of the website carefully
        - Take note of all visual elements, layout structures, and text content

        2. Overall Layout Description:
        - Number of columns
        - Positioning of major elements (header, navigation, main content area, sidebar, footer)
        - Grid systems or organizational structures

        3. Visual Elements Detail (for each element):
        - Size and position relative to other elements
        - Colors used (specific names or hex codes)
        - Shapes and styles (rounded corners, shadows, gradients)
        - Hover effects or animations (if visible)

        4. Text Content:
        - Include ALL text content in quotation marks
        - Headers, paragraphs, button labels, menu items, and other text

        5. CSS and Styling Details:
        - Fonts and font sizes
        - Text alignment
        - Spacing between elements
        - Padding and margins
        - Other CSS-related details

        6. Structured Sections:
        <Header>
        <Navigation>
        <Main Content>
        <Sidebar> (if applicable)
        <Footer>

        7. Final Review:
        - Check for missed elements or details
        - Consider recreation requirements
        - Add any helpful additional information

        Begin description:
        <website_description>
        """
        
        # Create the API request
        response = client.chat.completions.create(
            model="gpt-4o",  # Updated to the correct model name
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": default_prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500  # Adjust as needed
        )
        
        content = response.choices[0].message.content

        return content
        
        
    except FileNotFoundError:
        raise FileNotFoundError(f"Image file not found: {image_path}")
    except Exception as e:
        raise Exception(f"Error analyzing image: {str(e)}")
