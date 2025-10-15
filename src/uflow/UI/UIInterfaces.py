class IUINode(object):
    """docstring for IUINode."""

    def __init__(self):
        super(IUINode, self).__init__()

    def isReroute(self):
        return False

    def serializationHook(self):
        raise NotImplementedError("serializationHook of IUINode is not implemented")


class IPropertiesViewSupport(object):
    """docstring for IPropertiesViewSupport."""

    def __init__(self):
        super(IPropertiesViewSupport, self).__init__()

    def createPropertiesWidget(self, propertiesWidget):
        pass


class IDataExporter(object):
    """Data exporter/importer

    Editor data can be exported/imported to/from arbitrary formats
    """

    def __init__(self):
        super(IDataExporter, self).__init__()

    @staticmethod
    def creationDateString():
        raise NotImplementedError(
            "creationDateString method of IDataExporter is not implemented"
        )

    @staticmethod
    def version():
        raise NotImplementedError("version method of IDataExporter is not implemented")

    @staticmethod
    def displayName():
        raise NotImplementedError(
            "displayName method of IDataExporter is not implemented"
        )

    @staticmethod
    def toolTip():
        return ""

    @staticmethod
    def createImporterMenu():
        return True

    @staticmethod
    def createExporterMenu():
        return True

    @staticmethod
    def doImport(uflowInstance):
        raise NotImplementedError("doImport method of IDataExporter is not implemented")

    @staticmethod
    def doExport(uflowInstance):
        raise NotImplementedError("doExport method of IDataExporter is not implemented")
