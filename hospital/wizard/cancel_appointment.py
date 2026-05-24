import datetime

from odoo import fields, models, api


class CancelAppointment(models.TransientModel):
    _name = 'cancel.appointment'

    appointment_id = fields.Many2one("appointment",string="Appointment")
    reason = fields.Text(string="Reason for Cancellation")
    date_cancel= fields.Datetime(string="Cancellation Date")

    def action_cancel(self):
        if self.appointment_id:
            self.appointment_id.unlink()
        return {'type': 'ir.actions.act_window_close'}

    @api.model
    def default_get(self, fields):
        res = super(CancelAppointment, self).default_get(fields)
        res['date_cancel'] = datetime.date.today()
        return res