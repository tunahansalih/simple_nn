import requests
import argparse
import cv2
import os

# when attempting to download images from the web both the Python
# programming language and the requests library have a number of
# exceptions that can be thrown so let's build a list of them now
# so we can filter on them
EXCEPTIONS = set([IOError, FileNotFoundError,
                  requests.exceptions.RequestException, requests.exceptions.HTTPError,
                  requests.exceptions.ConnectionError, requests.exceptions.Timeout])

ap = argparse.ArgumentParser()
ap.add_argument('-t', '--term', required=True, help='search term')
ap.add_argument('-o', '--output', required=True, help='path to output images')

args = vars(ap.parse_args())

API_KEY = None
assert API_KEY

search_url = "https://api.cognitive.microsoft.com/bing/v7.0/images/search"
search_term = args['term']

MAX_RESULTS = 1000
GROUP_SIZE = 50

headers = {"Ocp-Apim-Subscription-Key": API_KEY}
params = {"q": search_term,
          "offset": 0,
          "count": GROUP_SIZE}

print(f"[INFO] searching BING API for '{search_term}'")

response = requests.get(search_url, headers=headers, params=params)
response.raise_for_status()
search_results = response.json()

result_count = min(search_results['totalEstimatedMatches'], MAX_RESULTS)
print(f"[INFO] {result_count} total result for '{search_term}'")

total = 0

for offset in range(0, result_count, GROUP_SIZE):
    # update the search parameters using the current offset, then
    # make the request to fetch the results
    print("[INFO] making request for group {}-{} of {}...".format(
        offset, offset + GROUP_SIZE, result_count))
    params["offset"] = offset
    search = requests.get(search_url, headers=headers, params=params)
    search.raise_for_status()
    results = search.json()
    print(f"[INFO] saving images for group {offset}-{offset + GROUP_SIZE} of {result_count}...")
    # loop over the results
    for v in results["value"]:
        # try to download the image
        try:
            # make a request to download the image
            print("[INFO] fetching: {}".format(v["contentUrl"]))
            r = requests.get(v["contentUrl"], timeout=30)

            # build the path to the output image
            ext = v["contentUrl"][v["contentUrl"].rfind("."):]
            p = os.path.sep.join([args["output"], f"{str(total).zfill(8)}{ext}"])

            # write the image to disk
            f = open(p, "wb")
            f.write(r.content)
            f.close()

        # catch any errors that would not unable us to download the
        # image
        except Exception as e:
            # check to see if our exception is in our list of
            # exceptions to check for
            if type(e) in EXCEPTIONS:
                print("[INFO] skipping: {}".format(v["contentUrl"]))
                continue

        # try to load the image from disk
        image = cv2.imread(p)

        # if the image is `None` then we could not properly load the
        # image from disk (so it should be ignored)
        if image is None:
            print("[INFO] deleting: {}".format(p))
            os.remove(p)
            continue

        # update the counter
        total += 1
