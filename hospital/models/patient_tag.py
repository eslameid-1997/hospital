from odoo import models, fields, api



class PatientTag(models.Model):
    _name = 'patient.tag'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Patient Tag'

    name = fields.Char(string='Name')
    active = fields.Boolean(default=True)
    color=fields.Integer(string='Color')

