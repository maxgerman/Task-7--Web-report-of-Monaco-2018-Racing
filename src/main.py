from flask import Flask, render_template, request, redirect, url_for, session
from src.drivers import Driver

app = Flask(__name__)
app.secret_key = '123'


@app.route('/report', methods=['GET', 'POST'])
def common_report():
    """
    Show the report for all drivers.
    Sort and set the order switch based on url for the template. 
    """
    if request.args.get('order') == 'desc':
        asc_order = False
    else:
        asc_order = True
    session['report_desc_switch'] = not asc_order

    if request.method == 'POST':
        if request.form.get('desc_switch'):
            session['report_desc_switch'] = True
            return redirect(url_for('common_report', order='desc'))
        else:
            session['report_desc_switch'] = False
            return redirect(url_for('common_report'))

    lines = Driver.print_report(asc=asc_order).split('\n')
    return render_template('report.html', lines=lines)


@app.route('/drivers', methods=['GET', 'POST'])
def list_drivers():
    """Show ordered driver list as 'name - abbreviation' """

    if request.method == 'POST':
        if request.form.get('desc_switch'):
            session['driver_desc_switch'] = True
            return redirect(url_for('list_drivers', order='desc'))
        else:
            session['driver_desc_switch'] = False
            return redirect(url_for('list_drivers'))

    driver_id = request.args.get('driver_id')
    if driver_id:
        drivers = Driver.get_by_id(driver_id)
    else:
        asc_order = False if request.args.get('order') == 'desc' else True
        drivers = Driver.all(asc=asc_order)
    return render_template('drivers.html', drivers=drivers)




@app.route('/')
def home():
    return redirect(url_for('common_report'))


if __name__ == '__main__':
    Driver.build_report()
    app.run()
