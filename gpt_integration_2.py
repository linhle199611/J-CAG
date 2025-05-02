import sublime
import sublime_plugin
import urllib.request
import json

class GptApiSecondCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # Get the selected text
        selected_text = self.get_selected_text()
        if not selected_text:
            sublime.error_message("Please select a block of code to verify:")
            return

        selected_text_with_prompt = "Verify each function working correctly given the Javadoc comment. Reply with Yes or No for each functon. If No, show short description: " + "\n" + selected_text
        # Show input panel with the selected text
        self.view.window().show_input_panel("Verify each function working correctly given the Javadoc comment:", selected_text_with_prompt, self.on_done, None, None)

    def get_selected_text(self):
        selected_text = ""
        for region in self.view.sel():
            if not region.empty():
                selected_text += self.view.substr(region)
        return selected_text

    def on_done(self, input_text):
        # Make the API request
        response = self.query_gpt(input_text)
        print(response)
        if response:
            # Insert the response in a new view
            self.show_response(response)
        else:
            sublime.error_message("Failed to get a response from GPT API.")

    def query_gpt(self, input_text):
        # Replace with your actual OpenAI API key and endpoint
        api_key = "YOUR_API_KEY"
        api_url = "https://api.openai.com/v1/chat/completions"

        print(input_text)

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        data = json.dumps({
            "model": "gpt-4",
            "messages": [{"role": "user", "content": input_text}],
            "max_tokens": 100
        }).encode('utf-8')


        # Make the API call using urllib
        req = urllib.request.Request(api_url, data=data, headers=headers)
        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode())
                gpt_reply = result['choices'][0]['message']['content']

                # Insert the response into the document
                #self.view.insert(edit, self.view.sel()[0].begin(), "\n\nGPT-4 Response:\n" + gpt_reply)
                return gpt_reply
        except urllib.error.HTTPError as e:
            sublime.error_message(f"Failed to connect to GPT API: {e.reason}")

    def show_response(self, response_text):
        sublime.message_dialog(response_text)


# Hello
