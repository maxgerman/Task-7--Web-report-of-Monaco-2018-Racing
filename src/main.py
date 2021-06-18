from flask import Flask, render_template, request
from src.drivers import Driver

app = Flask(__name__)


@app.route('/report')
def common_report():
    """Show common statistics of all drivers"""
    asc_order = False if request.args.get('order') == 'desc' else True
    return Driver.all(asc_order)


@app.route('/drivers')
def list_drivers():
    driver_id = request.args.get('driver_id')

    if driver_id:
        return Driver.get(driver_id)
    else:
        desc_order = True if request.args.get('order') == 'desc' else False
        drivers = sorted(Driver.driver_list, key=lambda d: d.name, reverse=desc_order)
        return '<br>'.join(driver.name + ' ' + driver.abbr for driver in drivers)


if __name__ == '__main__':
    Driver.build_report()
    app.run()
