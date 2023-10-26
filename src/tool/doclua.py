import json
import io
import sys

json_file = io.open('snippets.json', 'w')

# Aliases
aliases = {
	"context": ["mapargs"],
}

snippet_data = {}
active_type = ''
active_data = []
active_prefix = ''
active_key = ''
active_desc = ''

def generate_alias():
	# Get key before the '.' e.g. context.context_screen = context
	key_split = active_key.split('.')
	key = key_split[0]
	cmd = key_split[1]

	if(not key in aliases):
		return
	
	# loop aliases and copy data over
	for alias in aliases[key]:
		new_key = f"{alias}.{cmd}"
		snippet_data[new_key] = snippet_data[active_key]

def generate_body():
	body = ''

	match active_type:
		case 'type':
			body = active_key
		case 'field':
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
	global active_type

	if(active_key == ''):
		active_desc = ''
		active_data.clear()
		return

	# put together desc & prefix
	snippet_data[active_key]['prefix'] = active_key
	snippet_data[active_key]['description'] = active_desc.strip()

	# generate body
	snippet_data[active_key]['body'] = generate_body()

	# generate aliases
	generate_alias()

	# clear globals
	active_desc = ''
	active_key = ''
	active_data.clear()

	if(not keep_data):
		active_prefix = ''
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
		case 'field':
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

	# Match doc base (func, type, param, etc.)
	match doc_base:
		case 'function':
			new_prefix(doc, 'function')
			func_name = doc[2].strip()
			new_key(func_name)

		case 'type':
			new_prefix(doc, 'type')

		case 'field':
			doc_type = doc[1].strip() 		# @field #boolean reverse
			field_name = doc[2].strip()
			field_desc = ''

			if('parent' in doc_type):		# @field [parent=#gredom] #number SCREEN
				new_prefix(doc, 'field')
				field_name = doc[3].strip()
			else:
				if(len(doc) > 3):
					i = 3
					while i < len(doc):
						field_desc = f"{field_desc} {doc[i].strip()}"
						i = i + 1
			
			new_key(field_name)

			add_to_desc(field_desc)
			save_current_snippet(True)

		case 'param':
			param = ''
			doc_type = doc[1].strip()

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
	if (len(line) > 4 and line[3] == '@'):
		return process_descriptor(line)
	
	# Get first 3 lines of line
	split = line[:3]
	if (split == "-- "):
		text = line[3:].strip() 	# remove first 3 letters
		return add_to_desc(text)

	# check if new 'block' is next
	if (split == '---'):
		return save_current_snippet()

def main(doclua):
	docfile = open(doclua, 'r')
	
	# Loop each line in doclua file
	for line in docfile:
		process_line(line)

	# save the final snippet
	save_current_snippet()

	# print logs
	print("Generated snippets.json from doclua file")
	print(f"Entries: {len(snippet_data)}")

	# write to json file
	json_data = json.dumps(snippet_data, indent=4)
	json_file.write(json_data)

	docfile.close()
	json_file.close()

if __name__ == "__main__":
	doclua = sys.argv[1]
	main(doclua)