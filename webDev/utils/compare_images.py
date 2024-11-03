import base64
from openai import OpenAI
import os

def compare_images(image_path_model: str, image_path_recent_state: str) -> str:
    try:
        # Initialize OpenAI client
        client = OpenAI()

        if not os.path.exists(image_path_recent_state):
            return False

        
        # Function to encode the image
        def encode_image(image_path: str) -> str:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        
        # Encode the image
        base64_image_1 = encode_image(image_path_model)
        base64_image_2 = encode_image(image_path_recent_state)
        
        # Default prompt if none provided

        default_prompt = """
            both images are screenshots of a html page, first_image is the version 
            I want to achieve, second_image is the recent version, what do i have to 
            improve to achieve the state offirst_image ?  
            imagine you are the designer and describe the developer what he has to improve, 
            dont write any code, 
            dont do references to first_image, the developer does not know it
        """

        default_prompt= """
            You are an experienced web designer tasked with providing guidance to a developer on improving a webpage. You will be analyzing two screenshots of an HTML page:

            Your task is to compare these images and provide clear, concise instructions to the developer on how to improve the current version (represented by the second image) to match the desired version (represented by the first image).

            Important guidelines:
            1. Do not write any code.
            2. Do not make any references to the "first image" or "desired version" in your instructions. The developer is only aware of their current version.
            3. Focus on visual and structural improvements, not technical implementation details.

            Please follow these steps:

            1. Analyze both images carefully, identifying the key differences between them.
            2. Formulate clear, concise instructions for the developer, focusing on what needs to be changed visually and structurally.

            Remember to be clear, concise, and specific in your instructions, avoiding any technical jargon or implementation details.
                    """
        # default_prompt = """
        #     relate to the images as "first_image" and "second_image" which has colored icons?  
        # """
        
        # Use custom prompt if provided, otherwise use default
        
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
                                "url": f"data:image/jpeg;base64,{base64_image_1}"
                            }
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image_2}"
                            },
                        },
                    ]
                }
            ],
            max_tokens=3000  # Adjust as needed
        )
        
        content = response.choices[0].message.content

        return content
        
        
    except FileNotFoundError:
        raise FileNotFoundError(f"Image file not found: {image_path_model}")
    except Exception as e:
        raise Exception(f"Error analyzing image: {str(e)}")
