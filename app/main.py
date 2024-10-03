import json
import os
from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv

from openai import OpenAI

load_dotenv()
app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/navigate', methods=['POST'])
def navigation():
    user_input = request.form['nl_input']
    response = get_response(user_input)

    if response.message.tool_calls:
        tool_call, *_ = response.message.tool_calls
        args = json.loads(tool_call.function.arguments)
        page = args.get('page')
        return redirect(url_for(page))

    return render_template('error.html')


def get_response(nl_input: str):
    tools = [
        {
            "type": "function",
            "function": {
                "name": "navigate",
                "description": "Navigate to a page based on user input.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "page": {
                            "type": "string",
                            "enum": ["home", "about", "contact"],
                            "description": "The page to navigate to. For anything related to messaging, send the user to the contact page."
                                           "When a user seeks information about the site in general, send them to the about page. "
                                           "For anything else send them to the home page."
                        }
                    },
                    "required": ["page"],
                }
            }
        }
    ]
    response, *_ = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a navigation bot for a company website"},
            {"role": "user", "content": nl_input},
        ],
        tools=tools,
    ).choices
    return response


if __name__ == '__main__':
    app.run(debug=True)
