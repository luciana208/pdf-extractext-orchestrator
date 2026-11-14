from app.presentation.downloads import content_disposition, txt_filename


def test_cambia_la_extension_pdf_por_txt():
    assert txt_filename("informe.PDF") == "informe.txt"


def test_agrega_txt_si_no_termina_en_pdf():
    assert txt_filename("informe") == "informe.txt"


def test_header_con_respaldo_ascii_y_nombre_utf8():
    header = content_disposition("año.txt")
    assert 'filename="a?o.txt"' in header
    assert "filename*=UTF-8''a%C3%B1o.txt" in header
