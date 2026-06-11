import base64
import io

import xlsxwriter

from odoo import api, fields, models, tools


class PatientWizard(models.TransientModel):
    _name = 'patient.wizard'
    _description = 'Patient Wizard'

    patient_id = fields.Many2one("patient")

    def action_print_excel(self):
        self.ensure_one()
        appointments = self.env['appointment'].search([('patient_id', '=', self.patient_id.id)])
        excel_file = self._generate_excel_report(appointments)
        attachment = self._create_excel_attachment(excel_file)
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }

    def _generate_excel_report(self, appointments):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet("مواعيد المريض")
        worksheet.right_to_left()

        # استدعاء دالة العناوين والهيدرز
        self._write_excel_headers(workbook, worksheet)

        row_idx = 6
        start_sum_row = row_idx + 1

        # قاموس ذكي لترجمة الحالات ليكون التقرير بالكامل باللغة العربية
        state_translation = {
            'draft': 'مسودة',
            'in_consultation': 'في الاستشارة',
            'done': 'منتهي',
            'cancel': 'ملغي'
        }

        for appt in appointments:
            worksheet.set_row(row_idx, 20)

            # 1. العمود 0 (رقم الموعد): استخدمنا حقل reference من الموديل الخاص بك لمنع الـ TypeError
            worksheet.write(row_idx, 0, appt.reference or '', workbook.add_format({'align': 'center', 'border': 1}))

            # 2. العمود 1 (تاريخ الموعد): الحقل الفعلي في موديلك هو appointment_date
            worksheet.write(row_idx, 1, str(appt.appointment_date) if appt.appointment_date else '',
                            workbook.add_format({'align': 'center', 'border': 1}))

            # 3. العمود 2 (الطبيب المعالج): doctor_id.name سليم تماماً لأن doctor_id مربوط بـ res.users
            worksheet.write(row_idx, 2, appt.doctor_id.name if appt.doctor_id else '',
                            workbook.add_format({'align': 'right', 'border': 1}))

            # 4. العمود 3 (العيادة / القسم): غير موجود بموديلك حالياً، نتركه فارغاً مؤقتاً لحين إضافته مستقبلاً
            worksheet.write(row_idx, 3, '', workbook.add_format({'align': 'right', 'border': 1}))

            # 5. العمود 4 (حالة الموعد): ترجمة حالة الموعد إلى العربية
            worksheet.write(row_idx, 4, state_translation.get(appt.state, ''),
                            workbook.add_format({'align': 'center', 'border': 1}))

            # 6. العمود 5 (تكلفة الكشف): غير موجود بموديلك، نضع 0.0 مؤقتاً حتى لا تنكسر معادلة الـ SUM الإجمالية
            worksheet.write(row_idx, 5, 0.0,
                            workbook.add_format({'align': 'left', 'border': 1, 'num_format': '#,##0.00" ج.م"'}))

            row_idx += 1

        # سطر إجمالي تكاليف المواعيد
        worksheet.merge_range(row_idx, 0, row_idx, 4, "إجمالي تكاليف المواعيد",
                              workbook.add_format({'bold': True, 'bg_color': '#E6F2F2', 'border': 1, 'align': 'left'}))

        # معادلة الـ SUM لجمع عمود التكلفة (F)
        worksheet.write_formula(row_idx, 5, f"=SUM(F{start_sum_row}:F{row_idx})", workbook.add_format(
            {'bold': True, 'bg_color': '#E6F2F2', 'border': 1, 'num_format': '#,##0.00" ج.م"'}))

        workbook.close()
        output.seek(0)
        return output.read()

    def _write_excel_headers(self, workbook, worksheet):
        title_style = workbook.add_format({'bold': True, 'font_size': 14, 'font_color': '#005B5C', 'align': 'right'})
        header_style = workbook.add_format(
            {'bold': True, 'font_color': '#FFFFFF', 'bg_color': '#005B5C', 'align': 'center', 'border': 1})
        worksheet.merge_range('A1:F1', 'تقرير مواعيد المريض الشامل', title_style)
        worksheet.write('A3', 'اسم المريض:', workbook.add_format({'bold': True}))
        worksheet.write('B3', self.patient_id.name)
        headers = ["رقم الموعد", "تاريخ الموعد", "الطبيب المعالج", "العيادة / القسم", "حالة الموعد", "تكلفة الكشف"]
        for col_num, header in enumerate(headers):
            worksheet.write(5, col_num, header, header_style)
        column_widths = {'A': 15, 'B': 16, 'C': 20, 'D': 25, 'E': 15, 'F': 18}
        for col, width in column_widths.items():
            worksheet.set_column(f'{col}:{col}', width)

    def _create_excel_attachment(self, excel_file):
        return self.env['ir.attachment'].create({
            'name': f'مواعيد_{self.patient_id.name}.xlsx',
            'type': 'binary',
            'datas': base64.b64encode(excel_file),
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })