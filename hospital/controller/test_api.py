from requests import auth

from odoo import http, api


class TestApiController(http.Controller):

    @http.route('/api/test', methods=['GET'], type='http', auth='public', csrf=False)
    def test_endpoint(self, **kwargs):
        print("⚡ inside test method ⚡")
        return "Success"

