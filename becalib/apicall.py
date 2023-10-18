import requests
response = requests.get("https://api-gw.sovereignsolutions.com/gateway/routing/india/route/v1/bike/72.87959175878925,20.016468998748095;72.89543879785987,19.974327694670322;73.03632658976028,20.000264344928624?alternatives=false&steps=true&overview=simplified&api-key=6bb21ca2-5a4e-4776-b80a-87e2fbd6408d", verify=False)
print(response.content)
# key = '6bb21ca2-5a4e-4776-b80a-87e2fbd6408d'
# url = "https://api-gw.sovereignsolutions.com/gateway/routing/india/route/v1/bike/72.87959175878925,20.016468998748095;72.89543879785987,19.974327694670322;73.03632658976028,20.000264344928624?alternatives=false&steps=true&overview=simplified"
# # params = {"positions":[0,6,7,29]}
# headers = { "api-key" : key,
#             "Content-Type" : "application/json"}
# # Make a get request with the parameters.
# response = requests.get(url, headers=headers)

# # Print the content of the response
# print(response.content)

