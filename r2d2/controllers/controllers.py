# -*- coding: utf-8 -*-
from odoo import http

# class R2d2Patch(http.Controller):
#     @http.route('/r2d2_patch/r2d2_patch/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/r2d2_patch/r2d2_patch/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('r2d2_patch.listing', {
#             'root': '/r2d2_patch/r2d2_patch',
#             'objects': http.request.env['r2d2_patch.r2d2_patch'].search([]),
#         })

#     @http.route('/r2d2_patch/r2d2_patch/objects/<model("r2d2_patch.r2d2_patch"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('r2d2_patch.object', {
#             'object': obj
#         })