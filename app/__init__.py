from flask import Flask, render_template, redirect, url_for, flash
from flask_login import LoginManager, login_required
from werkzeug import exceptions

from config import config
from .database import SQLITE


db = SQLITE()
login_manager = LoginManager()


def init_data():
    from .models import User, PaymentMethod

    admin_exist = db.session.query(User).filter(User.email == "user1@test.com").first()
    if not admin_exist:
        User.init_data()
        PaymentMethod.init_data()


def create_app(config_name):

    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "login"

    # csrf.init_app(app)

    @app.errorhandler(exceptions.NotFound)
    def handle_NotFound(e):
        flash(f"Page introuvable.", category="danger")
        return redirect(url_for("dash.dashboard"))

    @login_manager.unauthorized_handler
    def unauthorized_handler():
        return redirect(url_for("auth.login"))

    @app.before_first_request
    def setup():
        db.create_all()
        init_data()

    # @app.after_request
    # def add_header(response):
    #     response.headers[
    #         "Strict-Transport-Security"
    #     ] = "max-age=63072000; includeSubDomains; preload"
    #     response.headers["X-Content-Type-Options"] = "nosniff"
    #     response.headers["X-Frame-Options"] = "SAMEORIGIN"
    #     response.headers[
    #         "Content-Security-Policy"
    #     ] = "connect-src self;font-src https://fonts.googleapis.com https://fonts.gstatic.com https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.2/;script-src 'self' https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/;base-uri 'self'"
    #     return response

    # @app.errorhandler(CSRFError)
    # def handle_csrf_error(e):
    #     return render_template("error.html", reason=e.description), 400

    @app.route("/")
    @login_required
    def index():
        return render_template("about.html")

    @app.route("/sw.js")
    def sw():
        return app.send_static_file("sw.js")

    from .sales import sales as sales_blueprint
    from .auth import auth as auth_blueprint
    from .dashboards import dash as dash_blueprint
    from .recovers import recovers as recovers_blueprint
    from .payments import payments as payments_blueprint
    from .reconciliations import reconciliations as reconciliations_blueprint
    from .stocks import stocks as stocks_blueprint
    from .purchasings import purchasings as purchasings_blueprint
    from .costs import costs as costs_blueprint
    from .companies import companies as companies_blueprint

    app.register_blueprint(auth_blueprint, url_prefix="/")
    app.register_blueprint(dash_blueprint, url_prefix="/")

    app.register_blueprint(sales_blueprint, url_prefix="/sales")
    app.register_blueprint(recovers_blueprint, url_prefix="/recovers")
    app.register_blueprint(payments_blueprint, url_prefix="/payments")
    app.register_blueprint(reconciliations_blueprint, url_prefix="/reconciliations")
    app.register_blueprint(stocks_blueprint, url_prefix="/stocks")
    app.register_blueprint(purchasings_blueprint, url_prefix="/purchasings")
    app.register_blueprint(costs_blueprint, url_prefix="/costs")
    app.register_blueprint(companies_blueprint, url_prefix="/companies")

    # *****************************************************************************************************

    @app.context_processor
    def utility_processor():
        import calendar
        from calendar import Calendar, monthrange
        from datetime import datetime, date, timedelta

        def get_workings_days():
            n = 0
            num_days = monthrange(today().year, today().month)[1]
            for i in range(num_days):
                d = today() + timedelta(days=i)
                if d.isoweekday() not in [6, 7]:
                    n += 1
            return n

        def today():
            return date.today()

        def dayDelta(dt, delta):
            return dt + timedelta(days=delta)

        def strftime(value, format):
            return value.strftime(format)

        def toDate(year, month, day):
            return datetime.strptime(f"{year}-{month}-{day}", "%Y-%m-%d").date()

        def isocalendar():
            return date.today().isocalendar()

        def format_price(amount, currency="€"):
            return "{0:.2f}{1}".format(amount, currency)

        def get_months():
            return list(calendar.month_name)

        def get_monthdates(year, month):
            obj = calendar.Calendar()
            li = []

            # iterating with itermonthdates
            for day in obj.itermonthdates(year, month):
                li.append(day)
            return li

        def get_monthdays_with_name(year, month):
            l = []
            for i in range(monthrange(year, month)[1]):
                l.append(
                    {
                        "number": i + 1,
                        "name": calendar.day_name[calendar.weekday(year, month, i + 1)],
                    }
                )
            return l

        return dict(
            format_price=format_price,
            get_months=get_months,
            get_monthdates=get_monthdates,
            get_monthdays_with_name=get_monthdays_with_name,
            toDate=toDate,
            today=today,
            dayDelta=dayDelta,
            isocalendar=isocalendar,
            strftime=strftime,
            get_workings_days=get_workings_days,
        )

    return app
