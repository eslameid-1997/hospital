from odoo import models, fields, api


class Appointment(models.Model):
    _name = 'appointment'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'appointment Records'
    _rec_name = 'patient_id'

    patient_id = fields.Many2one('patient',string='Patient')
    appointment_date = fields.Date(string="Appointment Date",default=fields.Date.context_today)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ], string='Gender', related='patient_id.gender')
    reference=fields.Char(string='Reference')
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Low'),
        ('2', 'High'),
        ('3', 'Very High')], string="Priority",
        help='Gives the sequence order when displaying a list of MRP documents.')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_consultation', 'In Consultation'),
        ('done', 'Done'),
        ('cancel', 'Cancel')], string="Status")
    doctor_id = fields.Many2one('res.users',string='Doctor')
    pharmacy_ids=fields.One2many('pharmacy.patient','appointment_id',string='Pharmacy')
    hide_sales_price=fields.Boolean(string='Hide Sales Price')
    image=fields.Image(string='Image')
    @api.onchange('patient_id')
    def _onchange_reference(self):
        self.reference=self.patient_id.reference

    def action_test(self):
        return {
            'effect':{
            'fadeout':'slow',
            'message':'Click Successful',
            'type':'rainbow_man'
        }
        }

    def action_in_consultation(self):
        for record in self:
            record.state='in_consultation'

    def action_done(self):
        for record in self:
            record.state='done'

    def action_cancel(self):
        for record in self:
            record.state='cancel'

    def action_reset_to_draft(self):
        for record in self:
            record.state='draft'


class Pharmacy(models.Model):
    _name = 'pharmacy.patient'
    _description = 'Pharmacy Records'

    product_id = fields.Many2one('product.product',string='Product')
    unit_price = fields.Float(string='Unit Price',related='product_id.list_price')
    qty = fields.Integer(string='Quantity')
    appointment_id = fields.Many2one('appointment',string='Appointment')
