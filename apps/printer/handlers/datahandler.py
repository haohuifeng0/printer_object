import logging
import os
import random
import string

import xlrd
from sqlalchemy.exc import IntegrityError
from xlrd import XLRDError

from apps.printer.handlers import RESPONSE
from apps.printer.handlers.RESPONSE import AppError
from apps.printer.handlers.base import BaseHandler
from libs.model import SendData


class DataHandler(BaseHandler):

    def post(self):
        try:
            try:
                upload_file = self.request.files.get('file')[0]
                logging.info("upload file to save data")
            except Exception as e:
                raise AppError(RESPONSE.ILLEGAL_FORMAT, {
                    'reason': f"Illegal format, body:{self.request.body}",

                })
            original_fname = upload_file['filename']
            extension = os.path.splitext(original_fname)[1]
            if extension not in ['.xlsx', '.xls']:
                raise AppError(RESPONSE.ILLEGAL_FORMAT)

            # write into tmp file
            fname = ''.join(random.choice(
                string.ascii_lowercase + string.digits) for _ in range(6))
            final_filename = fname + extension
            file_path = final_filename
            output_file = open(file_path, 'wb')
            output_file.write(upload_file['body'])
            output_file.close()

            # read from tmp file
            repeat_data = []
            try:
                wb = xlrd.open_workbook(file_path)
                for sheet in wb.sheets():
                    for j in range(sheet.nrows):
                        row = sheet.row_values(j)
                        try:
                            SendData(
                                db_code=str(row[0]),
                                ems_code=str(row[1]),
                                weight=float(row[2]),
                                good=str(row[3]),
                                recipient_name=str(row[4]),
                                recipient_phone=str(row[5]),
                                recipient_addr=str(row[6]),
                                comment=row[7] if len(row) > 8 else ''
                            ).save()
                        except IntegrityError:
                            repeat_data.append(str(row[0]))
            except XLRDError as e:
                raise AppError(RESPONSE.ILLEGAL_FORMAT, {
                    'reason': e
                })
            # remove tmp file
            os.remove(file_path)
            self.write_data(repeat_data)
        except AppError:
            raise
        except Exception as e:
            logging.exception("PRINTER post data exception : %s", e)
            self.write_ret(RESPONSE.SERVER_ERROR)

    def delete(self):
        try:
            SendData().delete_all(SendData)
            self.write_data()
        except AppError:
            raise
        except Exception as e:
            logging.exception("PRINTER delete all data exception : %s", e)
            self.write_ret(RESPONSE.SERVER_ERROR)
