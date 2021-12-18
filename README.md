# mac-device-id-to-model
A list of known Mac model identifiers, scraped from Apple Support, that you can use to determine a Mac's marketing name (including model year). This can be useful in managment or other scripts.

## Why not use the old methods?
```
curl -s https://support-sp.apple.com/sp/product?cc=` echo $DEVICE_SERIAL | cut -c 9-` 
```
This one doesn't work with Apple's (new serial number)[https://www.macrumors.com/2021/05/05/purple-iphone-12-randomized-serial-number/] format. They have not provided any alterntive.

```
Read some random plist files!
```
This changes each major OS version, and archtectecture, and is not reliable.
```
Use MDM!
```
Even if you use MDM, I do, you may find it useful to have the marketing name or model year in a shell script.

## How do I use it?
However you like! You can curl the raw GitHub URL to get the most up-to-date list, then search for the line containing your model identifier such as `iMac21,2`. 

Here's an example:
```
# Determine the model and year:
DEIVCE_IDENTIFIER=$(sysctl hw.model | awk '{print $NF}')
DEVICE_MODEL_CURL=$(curl -s "https://raw.githubusercontent.com/quacktacular/mac-device-id-to-model/main/models.txt")
if [[ $DEVICE_MODEL_CURL = *"("*")"* ]]; then
  DEVICE_MODEL=$( echo $DEVICE_MODEL_CURL | grep "$DEIVCE_IDENTIFIER" | cut -f1 -d"|" )	
  DEVICE_YEAR=$( echo "$DEVICE_MODEL" | grep -o -E '[0-9][0-9][0-9][0-9]' )
else
  DEVICE_MODEL="Unknown Mac"
  DEVICE_YEAR="N/A"
fi

# Now you can use the variables:
echo $DEVICE_MODEL
echo $DEVICE_YEAR
```

## Where does the data come from?
It's scraped from Apple's Support site. When new Mac models are released `update_models.py` can be run to create a new list. These articles are quite old, and if Apple makes breaking changes to the HTML the Python script might need to be adjusted a bit.

## My model is missing!
Run the script the make a new PR, or let me know...
