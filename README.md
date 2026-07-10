# mac-device-id-to-model

A list of known Mac model identifiers, scraped from Apple Support, that you can use to determine a Mac's marketing name (including model year). This can be useful in managment or other scripts.

## Why not use the old methods?

```
curl -s https://support-sp.apple.com/sp/product?cc=` echo $DEVICE_SERIAL | cut -c 9-`
```

This one doesn't work with Apple's [new serial number](https://www.macrumors.com/2021/05/05/purple-iphone-12-randomized-serial-number/) format. EG with newer Apple Silicon / M1 / M1 Pro / M1 Max / 2021 Macs. They have not provided any alterntive.

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
DEVICE_IDENTIFIER=$(sysctl hw.model | awk '{print $NF}')
DEVICE_MODEL_CURL=$(curl -s "https://raw.githubusercontent.com/quacktacular/mac-device-id-to-model/main/models.txt" \
  | grep "|$DEVICE_IDENTIFIER\| \+$DEVICE_IDENTIFIER" | head -1 | cut -f1 -d"|")
if [[ $DEVICE_MODEL_CURL = *"("*")"* ]]; then
  DEVICE_MODEL=$( echo $DEVICE_MODEL_CURL | cut -f1 -d"|" )
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

It's scraped from Apple's Support identify pages (URLs in `config.yaml`). Run:

```
pip install -r requirements.txt
python update_models.py                     # models.txt (default)
python update_models.py -f txt -f json      # both committed outputs
python update_models.py -f json -o out.json
```

Formats: `txt` (default), `csv`, `yaml`, `json` (`-f` is repeatable). Use `-o` for a single-format output path. Manual entries (e.g. MacBook Neo, until Apple publishes an identify page) also live in `config.yaml`.

A nightly GitHub Action re-scrapes and opens a PR when `models.txt` or `models.json` changes.

## My model is missing!

Run the script then make a new PR, or let me know...
