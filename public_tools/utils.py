DEFAULT_OPENOFFICE_PORT = 8100

import uno
from os.path import abspath, isfile, splitext

FAMILY_TEXT = "Text"
FAMILY_WEB = "Web"
FAMILY_SPREADSHEET = "Spreadsheet"
FAMILY_PRESENTATION = "Presentation"
FAMILY_DRAWING = "Drawing"

# ---------------------#
# Configuration Start #
# ---------------------#

# see http://wiki.services.openoffice.org/wiki/Framework/Article/Filter

# most formats are auto-detected; only those requiring options are defined here
IMPORT_FILTER_MAP = {
    "txt": {
        "FilterName": "Text (encoded)",
        "FilterOptions": "utf8"
    },
    "csv": {
        "FilterName": "Text - txt - csv (StarCalc)",
        "FilterOptions": "44,34,0"
    }
}

EXPORT_FILTER_MAP = {
    "pdf": {
        FAMILY_TEXT: {"FilterName": "writer_pdf_Export"},
        FAMILY_WEB: {"FilterName": "writer_web_pdf_Export"},
        FAMILY_SPREADSHEET: {"FilterName": "calc_pdf_Export"},
        FAMILY_PRESENTATION: {"FilterName": "impress_pdf_Export"},
        FAMILY_DRAWING: {"FilterName": "draw_pdf_Export"}
    },
    "html": {
        FAMILY_TEXT: {"FilterName": "HTML (StarWriter)"},
        FAMILY_SPREADSHEET: {"FilterName": "HTML (StarCalc)"},
        FAMILY_PRESENTATION: {"FilterName": "impress_html_Export"}
    },
    "odt": {
        FAMILY_TEXT: {"FilterName": "writer8"},
        FAMILY_WEB: {"FilterName": "writerweb8_writer"}
    },
    "doc": {
        FAMILY_TEXT: {"FilterName": "MS Word 97"}
    },
    "rtf": {
        FAMILY_TEXT: {"FilterName": "Rich Text Format"}
    },
    "txt": {
        FAMILY_TEXT: {
            "FilterName": "Text",
            "FilterOptions": "utf8"
        }
    },
    "ods": {
        FAMILY_SPREADSHEET: {"FilterName": "calc8"}
    },
    "xls": {
        FAMILY_SPREADSHEET: {"FilterName": "MS Excel 97"}
    },
    "csv": {
        FAMILY_SPREADSHEET: {
            "FilterName": "Text - txt - csv (StarCalc)",
            "FilterOptions": "44,34,0"
        }
    },
    "odp": {
        FAMILY_PRESENTATION: {"FilterName": "impress8"}
    },
    "ppt": {
        FAMILY_PRESENTATION: {"FilterName": "MS PowerPoint 97"}
    },
    "swf": {
        FAMILY_DRAWING: {"FilterName": "draw_flash_Export"},
        FAMILY_PRESENTATION: {"FilterName": "impress_flash_Export"}
    }
}

PAGE_STYLE_OVERRIDE_PROPERTIES = {
    FAMILY_SPREADSHEET: {
        # --- Scale options: uncomment 1 of the 3 ---
        # a) 'Reduce / enlarge printout': 'Scaling factor'
        "PageScale": 100,
        # b) 'Fit print range(s) to width / height': 'Width in pages' and 'Height in pages'
        # "ScaleToPagesX": 1, "ScaleToPagesY": 1000,
        # c) 'Fit print range(s) on number of pages': 'Fit print range(s) on number of pages'
        # "ScaleToPages": 1,
        "PrintGrid": False
    }
}


# -------------------#
# Configuration End #
# -------------------#

class DocumentConversionException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


    def convert(self, inputFile, outputFile):

        inputUrl = self._toFileUrl(inputFile)
        outputUrl = self._toFileUrl(outputFile)

        loadProperties = {"Hidden": True}
        inputExt = self._getFileExt(inputFile)
        if IMPORT_FILTER_MAP.has_key(inputExt):
            loadProperties.update(IMPORT_FILTER_MAP[inputExt])

        document = self.desktop.loadComponentFromURL(inputUrl, "_blank", 0, self._toProperties(loadProperties))
        try:
            document.refresh()
        except AttributeError:
            pass

        family = self._detectFamily(document)
        self._overridePageStyleProperties(document, family)

        outputExt = self._getFileExt(outputFile)
        storeProperties = self._getStoreProperties(document, outputExt)

        try:
            document.storeToURL(outputUrl, self._toProperties(storeProperties))
        finally:
            document.close(True)

    def _overridePageStyleProperties(self, document, family):
        if PAGE_STYLE_OVERRIDE_PROPERTIES.has_key(family):
            properties = PAGE_STYLE_OVERRIDE_PROPERTIES[family]
            pageStyles = document.getStyleFamilies().getByName('PageStyles')
            for styleName in pageStyles.getElementNames():
                pageStyle = pageStyles.getByName(styleName)
                for name, value in properties.items():
                    pageStyle.setPropertyValue(name, value)

    def _getStoreProperties(self, document, outputExt):
        family = self._detectFamily(document)
        try:
            propertiesByFamily = EXPORT_FILTER_MAP[outputExt]
        except KeyError:
            pass
        try:
            return propertiesByFamily[family]
        except KeyError:
            pass
    def _detectFamily(self, document):
        if document.supportsService("com.sun.star.text.WebDocument"):
            return FAMILY_WEB
        if document.supportsService("com.sun.star.text.GenericTextDocument"):
            # must be TextDocument or GlobalDocument
            return FAMILY_TEXT
        if document.supportsService("com.sun.star.sheet.SpreadsheetDocument"):
            return FAMILY_SPREADSHEET
        if document.supportsService("com.sun.star.presentation.PresentationDocument"):
            return FAMILY_PRESENTATION
        if document.supportsService("com.sun.star.drawing.DrawingDocument"):
            return FAMILY_DRAWING

    def _getFileExt(self, path):
        ext = splitext(path)[1]
        if ext is not None:
            return ext[1:].lower()

    def _toFileUrl(self, path):
        return uno.systemPathToFileUrl(abspath(path))


