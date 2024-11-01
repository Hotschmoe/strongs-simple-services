@codebase we are going to implement checkout on the ordering page. Users will select a service and then be prompted to pay in cash or with card. Card payments will be processed by stripe using payment intents. This will allow us to handle products and pricing in our business_config.json file.

we will also implement a subscription model. Users will be able to select a subscription plan and then be charged on a recurring basis. The subscription will have a start date, end date, and status. The status will be active, canceled, or expired. The subscription will also have a services used and services allowed. The services used will be the number of services that the user has used. The services allowed will be the number of services that the user is allowed to use.

if a user has an active subscription, the subscription order "card" on ordering page will not be an option, instead there will be a "card" in its place to order pickup and that card will show how many services are left in the current period.

give detailed updated to all files, including models.py, main.py, business_config.json, and any other files that are relevant to the changes.
