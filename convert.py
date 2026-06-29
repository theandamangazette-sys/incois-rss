import urllib.request
import json
import xml.etree.ElementTree as ET
import ssl
from datetime import datetime
from xml.sax.saxutils import escape

# URL of the INCOIS JSON endpoint
JSON_URL = "https://tsunami.incois.gov.in/itews/DSSProducts/OPR/past90days.json"

try:
    ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
    # Fetch JSON data
   response = urllib.request.urlopen(JSON_URL, context=ctx)
    data = json.loads(response.read().decode())

    # Create the RSS XML skeleton
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    
    # Feed metadata
    ET.SubElement(channel, "title").text = "INCOIS Tsunami Past 90 Days"
    ET.SubElement(channel, "link").text = "https://tsunami.incois.gov.in/"
    ET.SubElement(channel, "description").text = "Automated RSS feed conversion for INCOIS Tsunami alerts."
    ET.SubElement(channel, "lastBuildDate").text = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")

    # Assuming the JSON has an array of events under a key, or is a root array.
    # We loop over the features or items. (Adjust indexing if INCOIS structure changes)
    items = data if isinstance(data, list) else data.get("features", [])

    for entry in items:
        # Pull key properties out of the JSON (adapting common INCOIS structures)
        # Note: If fields are nested under 'properties', adjust code accordingly
        props = entry.get("properties", entry)
        
        # Build titles and descriptions
        title_text = f"Tsunami Alert/Info - Magnitude {props.get('magnitude', 'N/A')}"
        region = props.get("region", "Unknown Region")
        time_str = props.get("originTime", props.get("dateTime", "Unknown Time"))
        
        description_text = f"Region: {region}<br>Time: {time_str}<br>Depth: {props.get('depth', 'N/A')} km"
        
        # Create RSS Item element
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = escape(title_text)
        ET.SubElement(item, "description").text = escape(description_text)
        ET.SubElement(item, "guid", isPermaLink="false").text = str(props.get("id", time_str))
        
        # Parse date to standard RFC 822 format for RSS readers if possible
        try:
            # Assumes ISO-like string; if parsing fails, fallback to raw string
            clean_date = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
            ET.SubElement(item, "pubDate").text = clean_date.strftime("%a, %d %b %Y %H:%M:%S GMT")
        except:
            ET.SubElement(item, "pubDate").text = str(time_str)

    # Save format into xml file
    tree = ET.ElementTree(rss)
    ET.indent(tree, space="  ", level=0)  # Make XML pretty
    tree.write("tsunami.xml", encoding="utf-8", xml_declaration=True)
    print("Successfully generated tsunami.xml")

except Exception as e:
    print(f"Error processing feed: {e}")
