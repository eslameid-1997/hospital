from odoo import models, fields, api
from datetime import date



class Patient(models.Model):
    _name = 'patient'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Patient Records'
    _rec_name = 'name'

    name = fields.Char(string='Name', required=True,tracking=True)
    age = fields.Integer(string='Age',compute='_compute_age')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ], string='Gender', default='male')
    active = fields.Boolean(default=True)
    birth_date = fields.Date(string='Birth Date')
    reference=fields.Char(string='Reference')
    tags_ids = fields.Many2many('patient.tag',string='Tags')
    appointment_count = fields.Integer(string='Appointment Count')
    @api.model
    def create(self, vals):
        vals['reference'] = self.env['ir.sequence'].next_by_code('patient')
        return super(Patient, self).create(vals)

    def write(self, vals):
        print('Patient: write')
        if not self.reference:
            vals['reference'] = self.env['ir.sequence'].next_by_code('patient')
        return super(Patient, self).write(vals)

    @api.depends('birth_date')
    def _compute_age(self):
        today = date.today()
        for rec in self:
            if rec.birth_date:
                rec.age = today.year - rec.birth_date.year
            else:
                rec.age = 0

    def name_get(self):
        patient_list = []
        for record in self:
            name = record.reference+' '+ record.name
            patient_list.append((record.id, name))
        return patient_list
