
from flask import Flask, render_template, request, url_for, flash, redirect
import json
import openai
import os
from os.path import join, dirname, realpath

# Create an instance of the Flask class that is the WSGI application.
# The first argument is the name of the application module or package,
# typically __name__ when using a single module.
app = Flask(__name__)


# Load config values
basedir = os.path.abspath(os.path.dirname(__file__))
configFilePath = os.path.join(basedir, 'config.json')
with open(configFilePath) as config_file:
    _config_details = json.load(config_file)

# Flask route decorators map / and /hello to the hello function.
# To add other resources, create functions that generate the page contents
# and add decorators to define the appropriate resource locators for them.

@app.route('/', methods=('GET', 'POST'))
@app.route('/index', methods=('GET', 'POST'))
def index():
    completion = ''
    tokensCount = _config_details['DEFAULT_TOKENS_COUNT']

    if request.method == 'POST':
        prompt = request.form['prompt']
        tokensCount = request.form['tokensCount']

        if not prompt:
            #flash('A question or message is required!')
            pass
        else:
            # Call Az openAi service
            completion = postMessage(prompt, tokensCount)
    
    return render_template('index.html', completion=completion, tokensCount=tokensCount)

def postMessage(prompt, tokensCount):

    # Setting up the deployment name
    deployment_name = _config_details['COMPLETIONS_MODEL']

    # This is set to `azure`
    openai.api_type = "azure"

    # The API key for your Azure OpenAI resource.
    #openai.api_key = os.getenv("OPENAI_API_KEY")
    openai.api_key = _config_details["OPENAI_API_KEY"]

    # The base URL for your Azure OpenAI resource. e.g. "https://<your resource name>.openai.azure.com"
    openai.api_base = _config_details['OPENAI_API_BASE']

    # Currently OPENAI API have the following versions available: 2022-12-01
    openai.api_version = _config_details['OPENAI_API_VERSION']

    maxTokensCount = _config_details['MAX_TOKENS_COUNT']
    if tokensCount is None or tokensCount.strip() == '' \
        or int(tokensCount) < 1 or int(tokensCount) > maxTokensCount:
        tokensCount = maxTokensCount

    try:
        # Create a completion for the provided prompt and parameters
        # To know more about the parameters, checkout this documentation: https://learn.microsoft.com/en-us/azure/cognitive-services/openai/reference
        completion = openai.Completion.create(
                        prompt=prompt,
                        temperature=0,
                        max_tokens=tokensCount,
                        engine=deployment_name)

        # print the completion
        response = completion.choices[0].text.strip(" \n")
    
        # Here indicating if the response is filtered
        #if completion.choices[0].finish_reason == "content_filter":
        #    print("The generated content is filtered.")
        
        return response

    except openai.error.APIError as e:
        # Handle API error here, e.g. retry or log
        print(f"OpenAI API returned an API Error: {e}")

    except openai.error.AuthenticationError as e:
        # Handle Authentication error here, e.g. invalid API key
        print(f"OpenAI API returned an Authentication Error: {e}")

    except openai.error.APIConnectionError as e:
        # Handle connection error here
        print(f"Failed to connect to OpenAI API: {e}")

    except openai.error.InvalidRequestError as e:
        # Handle connection error here
        print(f"Invalid Request Error: {e}")

    except openai.error.RateLimitError as e:
        # Handle rate limit error
        print(f"OpenAI API request exceeded rate limit: {e}")

    except openai.error.ServiceUnavailableError as e:
        # Handle Service Unavailable error
        print(f"Service Unavailable: {e}")

    except openai.error.Timeout as e:
        # Handle request timeout
        print(f"Request timed out: {e}")

if __name__ == '__main__':
    # Run the app server on localhost:4449
    app.run('localhost', 4449)