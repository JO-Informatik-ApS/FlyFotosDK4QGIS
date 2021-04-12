from PyQt5.QtCore import Qt, QSortFilterProxyModel


class MultiFilterMode:
    AND = 0
    OR = 1


class MultiFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, *args, **kwargs):
        QSortFilterProxyModel.__init__(self, *args, **kwargs)
        self.filters = {}
        self.multi_filter_mode = MultiFilterMode.OR

    def setFilterByColumn(self, column, qregex):
        self.filters[column] = qregex
        self.invalidateFilter()

    def clearFilter(self, column):
        del self.filters[column]
        self.invalidateFilter()

    def clearFilters(self):
        self.filters = {}
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        if not self.filters:
            return True

        results = []
        for key, qregex in self.filters.items():
            text = ''
            index = self.sourceModel().index(source_row, key, source_parent)
            if index.isValid():
                text = self.sourceModel().data(index, Qt.DisplayRole)
                if text is None:
                    text = ''
            
            if qregex.indexIn(text) != -1:
                results.append(True)
            else:
                results.append(False)

        if self.multi_filter_mode == MultiFilterMode.OR:
            return any(results)
        return all(results)