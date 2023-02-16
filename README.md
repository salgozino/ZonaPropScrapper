# ZonaProp Scrapper
This python app is used to receive a URL of a property from ZonaProp and return the key parameters.

# Install
> docker-compose up --build -d

# Run
> docker-compose up

Then in localhost:8080 you can access the flask api that it's exposing 3 endpoints:
- / : where there is a welcome message. TODO: Update the message
- /get_fields : This endpoints receives the parameter url and scrapp the zonaprop property and return some key parameters.
- /get_fields_csv :  equal to get_fields but instead of a JSON, returns a CSV with the information.