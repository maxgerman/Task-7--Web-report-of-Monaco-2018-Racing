from flask import Flask, render_template, request, redirect, url_for, session
from src.drivers import Driver

app = Flask(__name__)
app.secret_key = '123'

@app.route('/report', methods=['GET', 'POST'])
def common_report():
    """Show common statistics of all drivers"""
    if request.args.get('order') == 'desc':
        asc_order = False
    else:
        asc_order = True
    session['desc_switch'] = not asc_order

    if request.method == 'POST':
        if request.form.get('desc_switch'):
            session['desc_switch'] = True
            return redirect(url_for('common_report', order='desc'))            
        else:
            session['desc_switch'] = False
            return redirect(url_for('common_report'))
            print('asc')

    lines = Driver.all(asc=asc_order).split('\n')
    return render_template('report.html', lines=lines)


@app.route('/drivers')
def list_drivers():
    """Show ordered driver list as 'name - abbreviation' """
    driver_id = request.args.get('driver_id')
    if driver_id:
        return Driver.get(driver_id)
    else:
        desc_order = True if request.args.get('order') == 'desc' else False
        drivers = sorted(Driver.driver_list, key=lambda d: d.name, reverse=desc_order)
        # return '<br>'.join(driver.name + ' ' + driver.abbr for driver in drivers)
        return render_template('drivers.html', drivers=drivers)



@app.route('/')
def home():
    return redirect(url_for('common_report'))

if __name__ == '__main__':
    Driver.build_report()
    app.run()
