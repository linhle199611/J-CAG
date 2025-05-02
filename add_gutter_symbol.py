import sublime
import sublime_plugin
import re
import urllib.request
import json

# Command to add a gutter icon
class AddGutterSymbolCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		function_pattern = r'^\s*(public|protected|private|static)?\s+[\w<>\[\],\s]+\s+\w+\s*\([^)]*\)\s*\{'
		self.view.erase_regions('java_bookmarks')
		entire_file = self.view.substr(sublime.Region(0, self.view.size()))
		regions = self.find_all_functions(entire_file) 
		#regions = self.view.find_all(function_pattern)
		#regions = sublime.Region(regions)

		print(regions)
		self.view.add_regions('java_bookmarks', regions, 'bookmark', 'bookmark', sublime.HIDDEN)

	def find_all_functions(self, text):
		function_pattern = re.compile(r'\b(public|private|protected|static|\s)*[\w<>\[\]]+\s+\w+\s*\([^)]*\)\s*\{')
		matches = [match.start() for match in function_pattern.finditer(text)]

		function_regions = []

		for start in matches:
			end = self.find_function_end(text, start)
			if end != -1:
				function_regions.append(sublime.Region(start, end))
		return function_regions

	def find_function_end(self, text, start_pos):
		open_braces = 0
		in_function = False

		for i in range(start_pos, len(text)):
			char = text[i]

			if char == '{':
				open_braces += 1
				in_function = True
			elif char == '}':
				open_braces -= 1

			if in_function and open_braces == 0:
				return i + 1 
		return -1

class GutterClickListener(sublime_plugin.EventListener):

    def on_hover(self, view, point, hover_zone):
    	if hover_zone == sublime.HOVER_GUTTER:
    		for region in view.get_regions('java_bookmarks'):
    			if view.line(region).contains(point):
    				view.show_popup("Click the symbol to generate JavaDoc comment", location=point, max_width=600)
    				break

    def on_text_command(self, view, command_name, args):
    	#print(command_name)
    	if command_name == "drag_select" and args and "event" in args:
    		event = args["event"]
    		point = view.window_to_text((event["x"], event["y"]))

    		if event["x"] < 30:
    			for region in view.get_regions('java_bookmarks'):
    				if region.contains(point):
    					function_start = region.begin()
    					function_end = region.end() #view.find(r'\}', function_start).end()
    					#function_end = self.find_function_end(region, function_start)
    					function_region =  sublime.Region(function_start, function_end)
    					view.sel().clear()
    					view.sel().add(function_region)
    					function_text = view.substr(function_region)
    					print(f"Selected function:\n{function_text.strip()}")
    					selected_text_and_prompt = "Generate JavaDoc comment for the following function. Reply with compact JavaDoc comment only:" + "\n\n" + function_text;
    					#print(selected_text_and_prompt)
    					response = self.query_gpt(selected_text_and_prompt)
    					if response:
    						view.run_command('insert_function_text', {
    							'insertion_point': function_start,
    							'function_text': response
    							})
    					else:
    						sublime.error_message("Failed to get a response from GPT API.")
    					break

    def query_gpt(self, input_text):
    	api_key = "YOUR_API_KEY"
    	api_url = "https://api.openai.com/v1/chat/completions"

    	headers = {
    		"Authorization": f"Bearer {api_key}",
    		"Content-Type": "application/json"
    	}

    	data = json.dumps({
    		"model": "gpt-4",
    		"messages": [{"role": "user", "content": input_text}],
    		"max_tokens":100
    		}).encode('utf-8')

    	req = urllib.request.Request(api_url, data=data, headers=headers)
    	try: 
    		with urllib.request.urlopen(req) as response:
    			result = json.loads(response.read().decode())
    			gpt_reply = result['choices'][0]['message']['content']
    			return gpt_reply
    	except urllib.error.HTTPError as e:
    		sublime.error_message(f"Failed to connect to GPT API: {e.reason}")

class InsertFunctionTextCommand(sublime_plugin.TextCommand):
	def run(self, edit, insertion_point, function_text):
		self.view.insert(edit, insertion_point, f"{function_text}\n")


