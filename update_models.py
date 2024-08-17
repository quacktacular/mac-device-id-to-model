import requests
import re
from bs4 import BeautifulSoup

# Set our path to the text file
models_file_path = "./models.txt"
# Empty the file for rewriting
open(models_file_path, 'w').close()
# Open the now empty file
models_file = open(models_file_path, 'a')

device_families = [
  "https://support.apple.com/en-us/108054", # iMac
  "https://support.apple.com/en-us/102869", # MacBook Air
  "https://support.apple.com/en-us/108052", # MacBook Pro
  "https://support.apple.com/en-us/102852", # Mac mini
  "https://support.apple.com/en-us/103257", # MacBook
  "https://support.apple.com/en-us/102887", # Mac Pro
  "https://support.apple.com/en-us/102231", # Mac Studio
]

for familyURL in device_families:
  # Parse the page
  page = requests.get(familyURL)
  soup = BeautifulSoup(page.content, "html.parser")

  # Log the title
  h1_tag = soup.find('h1')
  if h1_tag:
    print("Working on: " + h1_tag.get_text(strip=True))

  # Collect all relevant tags from the page
  all_tags = [tag for tag in soup.find_all(['strong', 'b', 'h2', 'p', 'div'])]

  # Handle the results
  results = soup.find_all(lambda tag: tag.name in ["strong", "b", "h2"] and ("(" in tag.text or "Mac" in tag.text) and ("model" not in tag.text))

  for model in results:
    model_name = model.get_text(strip=True)

    # Look for "Model Identifier" in subsequent tags  
    model_identifiers = ""
    for tag in model.find_next_siblings():
      if tag.get_text(strip=True) and "Model Identifier" in tag.get_text(strip=True):
        model_identifiers = tag.get_text(strip=True).replace("Model Identifier", '').replace(":", '').replace(', ', ' ').replace(';', '').strip()
        break
    if model_identifiers == "":
      for tag in model.find_parent().find_next_siblings():
        if tag.get_text(strip=True) and "Model Identifier" in tag.get_text(strip=True):
          model_identifiers = tag.get_text(strip=True).replace("Model Identifier", '').replace(":", '').replace(', ', ' ').replace(';', '').strip()
          break

    # Look for "Part Numbers" in subsequent tags  
    part_numbers = ""
    for tag in model.find_next_siblings():
      if tag.get_text(strip=True) and "Part Number" in tag.get_text(strip=True):
        part_numbers = tag.get_text(strip=True).replace("Part Numbers", '').replace("Part Number", '').replace(":", '').replace(";", ',').replace(",", '').strip()
        break
    if part_numbers == "":
      for tag in model.find_parent().find_next_siblings():
        if tag.get_text(strip=True) and "Part Number" in tag.get_text(strip=True):
          part_numbers = tag.get_text(strip=True).replace("Part Numbers", '').replace("Part Number", '').replace(":", '').replace(";", ',').replace(",", '').strip()
          break

    # Year info
    year_string = ""
    match = re.search(r'\b\d{4}\b', model_name)
    if match:
      year_string = match.group() 
    if year_string == "":
      # Get siblings of the model (so far just iMac Pro)
      siblings = model.find_parent().find_previous_siblings()
      for sibling in siblings:
        match = re.search(r'\b\d{4}\b', sibling.get_text(strip=True))
        if match:
          year_string = match.group() 
          break # first one should be the correct one

    # Print the data
    line = (model_name or "") + "|" + (model_identifiers or "") + "|" + (year_string or "") + "|" + (part_numbers or "")
    print(line)
    models_file.write(line + "\n")

# Close the file
models_file.close()
