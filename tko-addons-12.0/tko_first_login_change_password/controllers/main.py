from odoo import http
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.web.controllers.main import ensure_db, Home
from odoo.http import request
# from odoo.addons.password_security.controllers.main import PasswordSecurityHome


class FirstLoginAuthSignupHome(AuthSignupHome):

    @http.route()
    def web_login(self, *args, **kw):
        ensure_db()
        response = super(FirstLoginAuthSignupHome, self).web_login(*args, **kw)
        if not request.params.get('login_success'):
            return response
        # Now, I'm logging in for the second time or more
        if not request.env.user._first_login():
            return response
        # My login is for the first time, redirect to reset password
        request.env.user.action_signup_prepare()
        request.session.logout(keep_db=True)
        redirect = request.env.user.partner_id.signup_url
        return http.redirect_with_hash(redirect)
