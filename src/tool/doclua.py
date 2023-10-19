import json
import io
import sys

json_file = io.open('snippets.json', 'w')

snippet_data = {}
active_type = ''
active_data = []
active_prefix = ''
active_key = ''
active_desc = ''

def generate_body():
	body = ''

	match active_type:
		case 'type':
			body = active_key
		case 'function':
			body = active_key + '('

			if(not active_data): #param list is empty
				body = body + ')'
				return body

			i = 0
			last = len(active_data) - 1
			while i < len(active_data):
				param = active_data[i]
				idx = str(i + 1)
				elem = "${" + idx + ":" + param + '}' # ${1:tab}

				if (not i == last):
					elem = elem + ", "

				body = body + elem
				i = i + 1

			body = body + ')'

	return body

def add_to_desc(text):
	global active_desc
	active_desc = active_desc + f"{text}\n"

def new_key(key):
	global active_key
	snip_key = f"{active_prefix}.{key}"
	active_key = snip_key
	snippet_data[snip_key] = {}

def save_current_snippet(keep_data=False):
	global active_prefix
	global active_key
	global active_desc

	print('save', active_key)

	if(active_key == ''):
		active_desc = ''
		active_data.clear()
		return

	# put together desc & prefix
	snippet_data[active_key]['prefix'] = active_key
	snippet_data[active_key]['description'] = active_desc.strip()

	# generate body
	snippet_data[active_key]['body'] = generate_body()

	# clear globals
	active_desc = ''
	active_data.clear()

	if(not keep_data):
		active_prefix = ''
		active_key = ''
		active_type = ''

def new_prefix(doc, typ):
	global active_prefix
	global active_type
	prefix = doc[1].strip() # [parent=#canvas]
	match typ:
		case 'type':
			active_prefix = prefix
		case 'function':
			split = prefix.split("parent=#") # canvas]
			prefix = split[1][:-1] # canvas
			active_prefix = prefix

	active_type = typ

def process_descriptor(line):
	global active_data

	# get second half of string after splitting by @, split by space
	split = line.split('@')
	doc = split[1].split(' ')

	# get data from doc line
	doc_base = doc[0].strip()
	doc_type = doc[1].strip()

	# Match doc base (func, type, param, etc.)
	match doc_base:
		case 'function':
			save_current_snippet()
			new_prefix(doc, 'function')
			func_name = doc[2].strip()
			new_key(func_name)
		case 'type':
			save_current_snippet()
			new_prefix(doc, 'type')
		case 'field':
			if (active_prefix == ''): # new block - global vars we can't process
				return 				  # e.g. @field [parent=#gre] #string APP_ROOT
			
			field_name = doc[2].strip()
			new_key(field_name)

			field_desc = ''

			if(len(doc) > 3):
				i = 3
				while i < len(doc):
					field_desc = f"{field_desc} {doc[i].strip()}"
					i = i + 1

			add_to_desc(field_desc)
			save_current_snippet(True)
		case 'param':
			param = ''
			if('#' in doc_type):
				param = doc[2].strip()
			else:
				param = doc_type

			active_data.append(param)

			# add desc
			text = "@" + split[1].strip()
			add_to_desc(text)
		case 'module':
			pass
		case _:
			text = "@" + split[1].strip()
			add_to_desc(text)

def process_line(line):
	# Check if line has descriptor
	if ("@" in line):
		return process_descriptor(line)
	
	# Get first 3 lines of line
	split = line[:3]
	if (split == "-- "):
		text = line[3:].strip() # remove first 3 letters
		return add_to_desc(text)

	# check if new 'block' is next
	if (split == '---'):
		return save_current_snippet()

def main(doclua):
	docfile = open(doclua, 'r')
	
	for line in docfile:
		process_line(line)

	save_current_snippet()

	json_data = json.dumps(snippet_data, indent=4)
	json_file.write(json_data)

	docfile.close()

if __name__ == "__main__":
	doclua = sys.argv[1]
	main(doclua)