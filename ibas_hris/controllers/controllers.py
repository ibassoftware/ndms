# -*- coding: utf-8 -*-
from odoo import http

# class IbasHris(http.Controller):
#     @http.route('/ibas_hris/ibas_hris/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ibas_hris/ibas_hris/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ibas_hris.listing', {
#             'root': '/ibas_hris/ibas_hris',
#             'objects': http.request.env['ibas_hris.ibas_hris'].search([]),
#         })

#     @http.route('/ibas_hris/ibas_hris/objects/<model("ibas_hris.ibas_hris"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ibas_hris.object', {
#             'object': obj
#         })