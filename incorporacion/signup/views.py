import json, urllib.request
import requests
import textwrap
from django.shortcuts import render
from django.http import HttpResponse, FileResponse
from django.core.files.storage import FileSystemStorage
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Image, Spacer, Paragraph, Table, TableStyle, Frame, BaseDocTemplate,
    PageTemplate, Flowable)
from reportlab.platypus import CellStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from io import BytesIO


with urllib.request.urlopen("https://xinternet.co/signup/json/signup_example.json") as url:
    data = json.loads(url.read().decode())

filename = "Acta de incorporación-" + data['code'] + ".pdf"

pagesize = (letter)

class SignupPDF(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        doc = SimpleDocTemplate("incorporacion/" + filename, pagesize = pagesize, topMargin=1 * cm, bottomMargin=1 * cm)    # Directorio raíz de la app.

        def procesoPpal(Story):
            """ Creación del informe. """

            I = Image("incorporacion/signup/static/signup/logo-horizontal.jpg", width=136, height=42)
            titulo1 = Paragraph("ACTA DE INCORPORACIÓN O ACTUALIZACIÓN A LA RUTA SANITARIA", estilo['Titulo'])
            titulo2 = Paragraph("GS_FOR_017 Versión: 01", estilo['Titulo'])
            titulo3 = Paragraph("Fecha de Vigencia: 24/01/2017", estilo['Titulo'])

            t = Table(
                data = [
                    [I, titulo1, [titulo2, titulo3]]
                ],
                style=[
                    ('VALIGN',(0,0),(2,0),'CENTER'),
                    ('GRID',(0,0),(2,0),0.5,colors.gray),
                ], 
                colWidths=[144, 228, 178],
            )

            Story.append(t)
            Story.append(Spacer(0, 2))

            encabezado1 = Paragraph('''<b>Fecha de registro: </b>''' + data['registration_date'], estilo['Normal1'])
            encabezado2 = Paragraph('''<b>Procedimiento: </b>''' + data['procedure'], estilo['Normal1'])
            encabezado3 = Paragraph('''<b>Código: </b>''' + data['code'], estilo['Normal1'])

            t = Table(
                data = [
                    [encabezado1, encabezado2, encabezado3]
                ],
                style = [
                    ('VALIGN', (0,0),(0,0), 'CENTER'),
                    ('GRID', (0, 0),(2, 0), 0.5, colors.gray),
                ],
                colWidths=[175, 220, 155],
            )

            Story.append(t)
            Story.append(Spacer(0, 2))

            seccDatosUs1 = Paragraph('''<b>DATOS DEL USUARIO</b>''', estilo['Titulo'])
            seccDatosUs2 = Paragraph('''<b>Institución: </b>''' + data['user_data']['type'], estilo['Normal1'])
            seccDatosUs3 = Paragraph('''<b>Nombre o Razón Social: </b>''' + data['user_data']['name_headquarters'], estilo['Normal1'])
            seccDatosUs4 = Paragraph('''<b>NIT #: </b>''' + data['user_data']['commercial_id'], estilo['Normal1'])
            seccDatosUs5 = Paragraph('''<b>Nombre Comercial o Sede: </b>''' + data['user_data']['name_offfice'], estilo['Normal1'])

            t = Table(
                data = [
                    [seccDatosUs1, seccDatosUs2],
                    [seccDatosUs3, seccDatosUs4],
                    [seccDatosUs5, ""],
                ],
                style = [
                    ('GRID', (0, 0),(1, 1), 0.5, colors.gray),
                    ('BOX', (0, 2),(-1, -1), 0.5, colors.gray),
                    ('BOX', (0, 0),(1, 0), 1, colors.black),
                ],
                colWidths=[350, 200],
            )

            Story.append(t)

            seccDatosUs6 = Paragraph('''<b>Dirección recolección: </b>''' + data['user_data']['geoinformation']['address_collection'], estilo['Normal1'])
            seccDatosUs7 = Paragraph('''<b>Dir. correspondencia: </b>''' + data['user_data']['geoinformation']['address_correspondence'], estilo['Normal1'])
            seccDatosUs8 = Paragraph("El horario de prestación del servicio es de 07:00a.m. a 05:00p.m. en horario diurno y de 06:00p.m. a 05:00a.m. en horario nocturno, según la jornada establecida de acuerdo a la categoría del generador.", estilo['Normal1'])

            t = Table(
                data = [
                    [seccDatosUs6, seccDatosUs8],
                    [seccDatosUs7, ""],
                ],
                style = [
                    ('GRID', (0, 0),(0, 1), 0.5, colors.gray),
                    ('BOX', (1, 0),(-1, -1), 0.5, colors.gray),
                    ('SPAN', (1, 0),(1, 1)),
                    ('VALIGN', (1, 0), (-1, -1), 'CENTER'),
                ],
                colWidths=[200, 350],
            )

            Story.append(t)

            neighborhood = Paragraph('''<b>Barrio: </b>''' + data['user_data']['geoinformation']['neighborhood'] + " |", estilo['Normal1'])
            localidad = Paragraph('''<b>Localidad: </b>''' + data['user_data']['geoinformation']['district'], estilo['Normal1'])
            telefono = Paragraph('''<b>Teléfono #: </b>''' + data['user_data']['contact_phones'][0]['phone_number'] + " |", estilo['Normal1'])
            celular = Paragraph('''<b>Celular #: </b>''' + data['user_data']['contact_phones'][1]['phone_number'], estilo['Normal1'])

            t = Table(
                data = [
                    [[neighborhood, localidad], [telefono, celular]],
                ],
                style = [
                    ('GRID', (0, 0),(1, 0), 0.5, colors.gray),
                    ('VALIGN', (0, 0), (1, 0), 'CENTER'),
                ],
                colWidths=[300, 250],
            )

            Story.append(t)

            contacto1 = Paragraph('''<b>CONTACTO | Nombre y apellidos: </b>''' + data['user_data']['contacts'][0]['name'] + 
                ''' | <b>Documento: </b>''' + data['user_data']['contacts'][0]['id_type'] + " " + data['user_data']['contacts'][0]['id'] + 
                ''' | <b>Teléfono: </b>''' + data['user_data']['contacts'][0]['phone'] + 
                ''' | <b>Correo electrónico: </b>''' + data['user_data']['contacts'][0]['email'], estilo['Normal1'])
            contacto2 = Paragraph('''<b>CONTACTO | Nombre y apellidos: </b>''' + data['user_data']['contacts'][1]['name'] + 
                ''' | <b>Documento: </b>''' + data['user_data']['contacts'][1]['id_type'] + " " + data['user_data']['contacts'][1]['id'] + 
                ''' | <b>Teléfono: </b>''' + data['user_data']['contacts'][1]['phone'] + 
                ''' | <b>Correo electrónico: </b>''' + data['user_data']['contacts'][1]['email'], estilo['Normal1'])
            repLegal1 = Paragraph('''<b>REPRESENTANTE LEGAL | </b> Nombre y apellidos: ''' + 
                data['user_data']['legal_owners'][0]['name'] + " | " + '''<b>Documento: </b>''' + 
                data['user_data']['legal_owners'][0]['id_type'] + " " + 
                data['user_data']['legal_owners'][0]['id'] + ''' <b>(FIRMA AUTORIZADA) | Teléfono: </b>''' + 
                data['user_data']['legal_owners'][0]['contact_phones'][0]['phone_number'] + ", " + 
                data['user_data']['legal_owners'][0]['contact_phones'][1]['phone_number'] + ''' | <b>Correo electrónico: </b>''' + 
                data['user_data']['legal_owners'][0]['email'], estilo['Normal1'])
            repLegal2 = Paragraph('''<b>Nombre y apellidos: </b>''' + 
                data['user_data']['legal_owners'][1]['name'] + " | " + '''<b>Documento: </b>''' + 
                data['user_data']['legal_owners'][1]['id_type'] + " " + 
                data['user_data']['legal_owners'][1]['id'] + ''' | <b>Teléfono: </b>''' + 
                data['user_data']['legal_owners'][1]['contact_phones'][0]['phone_number'] + ", " + 
                data['user_data']['legal_owners'][1]['contact_phones'][1]['phone_number'] + ''' | <b>Correo electrónico: </b>''' + 
                data['user_data']['legal_owners'][1]['email'], estilo['Normal1'])
            
            t = Table(
                data = [
                    [contacto1],
                    [contacto2],
                    [repLegal1],
                    [repLegal2],
                ],
                style = [
                    ('BOX', (0, 0),(0, 3), 0.5, colors.gray),
                ],
                colWidths=[550],
            )
    
            Story.append(t)
            Story.append(Spacer(0, 2))

            # SECCIÓN CARACTERIZACIÓN DEL USUARIO

            caractUsuario = Paragraph('''<b>CARACTERIZACIÓN DEL USUARIO</b>''', estilo['Titulo'])
            userType = Paragraph('''<b>Tipo de servicio: </b>''' + data['user_type']['service_type'] + 
                ''' | <b>Tipo de actividad: </b>''' + data['user_type']['activity_type'] + 
                ''' | <b>Tipo de subactividad: </b>''' + data['user_type']['sub_activity_type'], estilo['Normal1'])
            
            t = Table(
                data = [
                    [caractUsuario],
                    [userType],
                ],
                style = [
                    ('BOX', (0, 0),(0, 0), 1, colors.black),
                    ('GRID', (0, 1),(0, 1), 0.5, colors.gray),
                ],
                colWidths=[550],
            )

            Story.append(t)

            catSrvSanitario01 = Paragraph('''<b>Categoría de Servicio </b>''' + data['user_type']['categorization'][0]['category_name'] + ":", estilo['Normal1'])
            categoryLevel01 = Paragraph(data['user_type']['categorization'][0]['category_level'], estilo['catLevel'])
            rangoAforo01 = Paragraph('''<b>Rango de Aforo: </b> ''' + data['user_type']['categorization'][0]['category_capacity'] + " " +
                data['user_type']['categorization'][0]['category_units'], estilo['Normal1'])
            
            catSrvSanitario02 = Paragraph('''<b>Categoría de Servicio </b>''' + data['user_type']['categorization'][1]['category_name'] + ":", estilo['Normal1'])
            categoryLevel02 = Paragraph(data['user_type']['categorization'][1]['category_level'], estilo['catLevel'])
            rangoAforo02 = Paragraph('''<b>Rango de Aforo: </b> ''' + data['user_type']['categorization'][1]['category_capacity'] + " " +
                data['user_type']['categorization'][1]['category_units'], estilo['Normal1'])

            catSrvSanitario03 = Paragraph("Otros tipos de residuo:", estilo['Normal1'])
            catOtros = Paragraph(data['user_type']['categorization'][2]['category_name'], estilo['catLevel'])
            categoryLevel03 = Paragraph(data['user_type']['categorization'][2]['category_level'], estilo['catLevel'])
            rangoAforo03 = Paragraph(data['user_type']['categorization'][2]['category_capacity'] + " " +
                data['user_type']['categorization'][2]['category_units'], estilo['Normal1'])
            
            t = Table(
                data = [
                    [[[catSrvSanitario01], [categoryLevel01], [rangoAforo01]],
                    [[catSrvSanitario02], [categoryLevel02], [rangoAforo02]],
                    [[catSrvSanitario03], [catOtros], [categoryLevel03], [rangoAforo03]]],
                ],
                style = [
                    ('GRID', (0, 0),(2, 0), 0.5, colors.gray),
                    ('VALIGN',(0,0),(2,0),'TOP'),
                ],
                colWidths=[182, 186, 182],
            )

            Story.append(t)

            observaciones1 = Paragraph('''<b>Observaciones: </b>''' + data['comments'], estilo['Normal1'])
            observaciones2 = Paragraph("La asignación de frecuencia de recolección estará sujeta a verificación por parte del Area Operativa", estilo['Titulo'])
            Nota1 = Paragraph('''<b>NOTA:</b> El usuario manifiesta conocer las condiciones de prestación del servicio de recolección, tratamiento y transporte hasta el sitio de disposición final, de los residuos hospitalarios y similares, las tarifas, frecuencias de recolección y características del servicio, así como el diligenciamiento del presente documento y avala con su firma haber recibido dicha información en forma clara y precisa.''', estilo['Normal1'])
            Nota2 = Paragraph("Los residuos de tipo Anatomopatológico, Cortopunzante y de Animales serán tratados por medio de proceso de Termodestrucción con gestores autorizados y los residuos de tipo Biosanitario serán tratados por proceso de Esterilización de Calor Húmedo por Ecocapital.", estilo['Normal1'])
            Nota3 = Paragraph("En caso de incumplimiento en el pago del servicio mayor a (3) tres periodos de facturación, el generador autoriza expresamente a Ecocapital por medio de este documento a ser reportado como deudor en las centrales de riesgo.", estilo['Normal1'])

            t = Table(
                data = [
                    [observaciones1],
                    [observaciones2],
                    [Nota1],
                    [Nota2],
                    [Nota3],
                ],
                style = [
                    ('GRID', (0, 0),(0, 1), 0.5, colors.gray),
                    ('BOX', (0, 2),(0, -1), 0.5, colors.gray),
                ],
                colWidths=[550],
            )

            Story.append(t)

            firma1 = Paragraph("Firma", estilo['Normal1'])
            firmaCliente = Paragraph("Nombre y sello del usuario " + data['signatures'][1]['name'], estilo['Normal1'])
            idCliente = Paragraph(data['signatures'][1]['id_type'] + " " + data['signatures'][1]['id'], estilo['Normal1'])
            firma2 = Paragraph("Firma", estilo['Normal1'])
            nombreEmpleado = Paragraph("Nombre del funcionario de Ecocapital " + data['signatures'][3]['name'], estilo['Normal1'])
            roleEmpleado = Paragraph("Cargo: " + data['signatures'][3]['role'], estilo['Normal1'])

            t = Table(
                data = [
                    [[firma1], [firma2]],
                    [[[firmaCliente], [idCliente]], [[nombreEmpleado], [roleEmpleado]]],
                ],
                style = [
                    ('BOX', (0, 0),(1, 1), 0.5, colors.gray),
                    ('BOTTOMPADDING', (0, 0),(1, 0), 25),
                ],
                colWidths=[275, 275],
            )

            Story.append(t)

            nota4 = Paragraph('''<b>NOTA: </b> Ecocapital certifica que el firmante de esta acta asistió a la conferencia <b>"Gestión Integral de los residuos generados en la atención a la salud y otras actividades",</b> la cual tiene un periodo de vigencia de un (1) año a partir de la firma de este documento.''', estilo['Normal1'])
            pieForm = Paragraph("ECOCAPITAL | NIT 900.487.187-3 | Carrera 19A No 61-11 | PBX 7462686 | servicio@ecocapital-sa.com", estilo['Normal1'])

            t = Table(
                data = [
                    [nota4],
                    [pieForm],
                ],
                style = [
                    ('BOX', (0, 0),(0, 0), 0.5, colors.gray),
                    ('TOPPADDING', (0, 1),(0, 1), 10),
                ],
                colWidths=[550],
            )
            
            Story.append(t)
            return Story


        # Código principal

        estilo = getSampleStyleSheet()

        estilo.add(ParagraphStyle(name = "Titulo", alignment=TA_CENTER, fontSize=10, fontName="Helvetica-Bold"))
        estilo.add(ParagraphStyle(name = "Titulo1", alignment=TA_LEFT, fontSize=10, fontName="Helvetica-Bold"))
        estilo.add(ParagraphStyle(name = "Titulo2", alignment=TA_LEFT, fontSize=10, fontName="Helvetica"))

        estilo.add(ParagraphStyle(name = 'Normal1', aligment=TA_LEFT, fontSize=9, fontName="Helvetica"))
        estilo.add(ParagraphStyle(name = 'catLevel', aligment=TA_LEFT, fontSize=9, fontName="Helvetica-Bold"))
        
        Story = []

        procesoPpal(Story)

        doc.build(Story)

        fs = FileSystemStorage("incorporacion")
        with fs.open(filename) as pdf:
            response = HttpResponse(pdf, content_type = 'application/pdf')
            response['Content-Disposition'] = 'attachment; filename=' + filename
            return response
        
        return response
