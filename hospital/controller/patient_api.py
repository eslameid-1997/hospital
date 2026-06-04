import json
import math
from odoo import http
from odoo.http import request, Response


# --- دالة الرد الناجح المصححة لأودو 15 ---
def validate_response(status, data, message, pagination=None):
    response_body = {
        "status": status,
        "message": message,
        "data": data
    }
    if pagination:
        response_body["pagination"] = pagination

    # 1. بنعمل الـ response عادي من غير ما نمرر status جواه
    response = request.make_response(
        json.dumps(response_body),
        headers=[('Content-Type', 'application/json')]
    )
    # 2. بنحدد الـ status code على الـ object نفسه هنا
    response.status = str(status)
    return response


# --- دالة الرد الخاطئ المصححة لأودو 15 ---
def invalidate_response(status, message):
    response_body = {
        "status": status,
        "message": message,
    }

    # 1. بنعمل الـ response عادي من غير ما نمرر status جواه
    response = request.make_response(
        json.dumps(response_body),
        headers=[('Content-Type', 'application/json')]
    )
    # 2. بنحدد الـ status code على الـ object نفسه هنا
    response.status = str(status)
    return response


class PatientApiController(http.Controller):

    # 1. جلب كل المرضى مع الـ Pagination (تم تحويلها لـ http لسهولة الـ GET)
    @http.route('/v1/patients', methods=['GET'], type='http', auth='public', csrf=False)
    def get_all_patients(self, **kwargs):
        patient_count = request.env["patient"].sudo().search_count([])

        # قراءة البارامترز وتأمين قيمها الرقمية
        try:
            page = int(kwargs.get('page', 1))
            limit = int(kwargs.get('limit', 4))
        except ValueError:
            page = 1
            limit = 4

        if page <= 0: page = 1
        if limit <= 0: limit = 10

        offset = (page - 1) * limit
        patients = request.env["patient"].sudo().search([], limit=limit, offset=offset)

        val_list = []
        for patient in patients:
            val_list.append({
                'id': patient.id,
                'name': patient.name,
                'gender': patient.gender,
                'birth_date': str(patient.birth_date) if patient.birth_date else False
            })

        total_pages = math.ceil(patient_count / limit) if patient_count > 0 else 1

        pagination_data = {
            'current_page': page,
            'limit_per_page': limit,
            'total_records': patient_count,
            'total_pages': total_pages
        }

        return validate_response(status=200, data=val_list, message="successful", pagination=pagination_data)

    @http.route('/v1/patient', methods=['POST'], type='http', auth='public', csrf=False)
    def create_patient(self, **kwargs):
        # 1. قراءة البيانات بأمان داخل try لتجنب الانهيار إذا كان الـ Body فارغاً
        try:
            body = request.httprequest.data.decode('utf-8')
            vals = json.loads(body) if body else {}
        except Exception:
            return Response(json.dumps({"status": 400, "message": "Invalid JSON or empty body"}),
                            content_type='application/json', status=400)

        # 2. التحقق من وجود بيانات
        if not vals:
            return Response(json.dumps({"status": 400, "message": "Missing request body"}),
                            content_type='application/json', status=400)

        try:
            cr = request.env.cr
            query = """ INSERT INTO patient (name, gender, birth_date)
                        VALUES ('Wael mohamed', 'male', '2001-06-12') 
                        RETURNING id, name, gender, birth_date; """

            # التنفيذ بشكل منفصل
            cr.execute(query)
            # جلب النتيجة في سطر مستقل
            res = cr.fetchone()

            if res:
                result_data = {
                    "status": 201,
                    "message": "Patient created successfully",
                    "data": {
                        "id": res[0],
                        "name": res[1],
                        "gender": res[2],
                        "birth_date": str(res[3])
                    }
                }
                return Response(json.dumps(result_data), content_type='application/json', status=201)

        except Exception as e:
            return Response(json.dumps({"status": 500, "message": str(e)}),
                            content_type='application/json', status=500)

        return Response(json.dumps({"status": 400, "message": "Failed to create patient"}),
                        content_type='application/json', status=400)
    #
    @http.route('/v1/patient', methods=['GET'], type='http', auth='public', csrf=False)
    def get_patient(self, **kwargs):
        patient_id = kwargs.get('id')
        if not patient_id:
            return invalidate_response(status=400, message="Missing 'id' parameter")

        try:
            patient = request.env["patient"].sudo().search([('id', '=', int(patient_id))], limit=1)
        except ValueError:
            return invalidate_response(status=400, message="Invalid 'id' format")

        if not patient:
            return invalidate_response(status=404, message="Patient not found")

        patient_data = {
            'id': patient.id,
            'name': patient.name,
            'gender': patient.gender,
            'birth_date': str(patient.birth_date) if patient.birth_date else False
        }

        return validate_response(status=200, data=patient_data, message="successful")

    # 4. تحديث بيانات المريض
    @http.route('/v1/patient/update', methods=['PUT'], type='json', auth='public', csrf=False)
    def update_patient(self, **kwargs):
        vals = request.jsonrequest
        patient_id = vals.get('id')
        if not patient_id:
            return {"status": 400, "message": "Missing patient ID"}

        patient = request.env["patient"].sudo().browse(int(patient_id))
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

    # 5. حذف مريض
    @http.route('/v1/patient/delete', methods=['DELETE'], type='json', auth='public', csrf=False)
    def delete_patient(self, **kwargs):
        vals = request.jsonrequest
        patient_id = vals.get('id')
        if not patient_id:
            return {"status": 400, "message": "Missing patient ID"}

        patient = request.env["patient"].sudo().browse(int(patient_id))
        if patient.exists():
            name = patient.name
            patient.unlink()
            return {
                "status": 200,
                "message": f"Patient {name} deleted successfully"
            }
        return {"status": 404, "message": "Patient not found"}


