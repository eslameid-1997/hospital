import json
from requests import auth
from odoo import http, api
from odoo.http import request


class PatientApiController(http.Controller):

    @http.route('/v1/patient', methods=['POST'], type='json', auth='public', csrf=False)
    def test_endpoint(self, **kwargs):
        args=request.httprequest.data.decode()
        vals=json.loads(args)
        res=request.env["patient"].sudo().create(vals)
        if res:
            return {
                "status": 200,
                "message": "Patient created successfully",
                "id": res.id
            }

        return {
            "status": 400,
            "message": "Failed to create patient"
        }

    @http.route('/v1/patients', methods=['GET'], type='json', auth='public', csrf=False)
    def get_all_patients(self, **kwargs):
        # التصحيح: حطينا [] جوه الـ search
        patients = request.env["patient"].sudo().search([])

        valList = []
        for patient in patients:
            valList.append({
                'id': patient.id,
                'name': patient.name,
                'gender': patient.gender,
                'birth_date': str(patient.birth_date) if patient.birth_date else False
            })
        return {
            'status': 200,
            'total_count': len(valList),
            'patients': valList
        }

    @http.route('/v1/patient/update', methods=['PUT'], type='json', auth='public', csrf=False)
    def update_patient(self, **kwargs):
        vals = request.jsonrequest
        patient_id = vals.get('id')
        if not patient_id:
            return {"status": 400, "message": "Missing patient ID"}
        patient = request.env["patient"].sudo().browse(patient_id)
        if patient.exists():
            patient.write({
                'name': vals.get('name', patient.name),
                'gender': vals.get('gender', patient.gender),
                'birth_date': vals.get('birth_date', patient.birth_date)
            })
            return {
                "status": 200,
                "message": f"Patient {patient.name} updated successfully"
            }
        return {"status": 404, "message": "Patient not found"}

    @http.route('/v1/patient/delete', methods=['DELETE'], type='json', auth='public', csrf=False)
    def delete_patient(self, **kwargs):
        vals = request.jsonrequest
        patient_id = vals.get('id')
        if not patient_id:
            return {"status": 400, "message": "Missing patient ID"}
        patient = request.env["patient"].sudo().browse(patient_id)
        if patient.exists():
            name = patient.name
            patient.unlink()
            return {
                "status": 200,
                "message": f"Patient {name} deleted successfully"
            }
        return {"status": 404, "message": "Patient not found"}




