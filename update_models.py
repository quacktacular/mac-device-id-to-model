import requests
from bs4 import BeautifulSoup

# Set our path to the text file
models_file_path = "./models.txt"
# Empty the file for rewriting
open(models_file_path, 'w').close()
# Open the now empty file
models_file = open(models_file_path, 'a')

device_families = ["https://support.apple.com/en-ca/HT201634", # MacBook Pro
	"https://support.apple.com/en-ca/HT201862", # MacBook Air
	"https://support.apple.com/en-ca/HT201300", # iMac
	"https://support.apple.com/en-ca/HT201894", # Mac mini
	"https://support.apple.com/en-us/HT201608", # MacBook
	"https://support.apple.com/en-us/HT202888", # Mac Pro
	"https://support.apple.com/en-ca/HT213073", # Mac Studio 
]
for familyURL in device_families:
	page = requests.get(familyURL)
	soup = BeautifulSoup(page.content, "html.parser")
	results = soup.findAll(lambda tag:tag.name=="strong" and "(" in tag.text)
	for model in results:
		model_name = str(model).replace('<strong>','').replace('</strong>','').replace('<br/>','').strip()
		section = model.find_parent('p')
		model_identifers = ""
		for line in section:
			if "Model" in line:
					model_identifers = str(line).replace("Model Identifier:",'').replace(", ",' ').replace(", ",' ').strip()
					break
		print(model_name + "|" + model_identifers)
		models_file.write(model_name + "|" + model_identifers + "\n")

# Close the file
models_file.close()
