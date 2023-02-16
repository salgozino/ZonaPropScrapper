import csv
from io import StringIO
from flask import Flask, request, make_response
from scrapper import Scrapper

app = Flask(__name__)


def dict_to_csv(data_dict):
    csv_data = []
    header = []
    values = []
    for key, value in data_dict.items():
        header.append(key)
        values.append(value)
    csv_data.append(header)
    csv_data.append(values)

    si = StringIO()
    cw = csv.writer(si)
    cw.writerows(csv_data)
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=export.csv"
    output.headers["Content-type"] = "text/csv"
    return output


@app.route("/")
def index():
    return "This is a scrapper for ZonaProp, please use the get_fields page passing an URL of the departament that you want the information."


@app.route('/get_fields_csv')
def get_fields_csv():
    url = request.args.get("url")
    scrapper = Scrapper(url)
    data = scrapper.get_property()
    return dict_to_csv(data)


@app.route('/get_fields')
def get_fields():
    url = request.args.get("url")
    scrapper = Scrapper(url)
    return scrapper.get_property()


if __name__ == "__main__":
    app.run(host='0.0.0.0')
