# -*- coding: utf-8 -*-
from odoo import http

# class IbasMaterialrequest(http.Controller):
#     @http.route('/ibas_materialrequest/ibas_materialrequest/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ibas_materialrequest/ibas_materialrequest/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ibas_materialrequest.listing', {
#             'root': '/ibas_materialrequest/ibas_materialrequest',
#             'objects': http.request.env['ibas_materialrequest.ibas_materialrequest'].search([]),
#         })

#     @http.route('/ibas_materialrequest/ibas_materialrequest/objects/<model("ibas_materialrequest.ibas_materialrequest"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ibas_materialrequest.object', {
#             'object': obj
#         })